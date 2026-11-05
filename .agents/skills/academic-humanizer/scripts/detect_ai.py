#!/usr/bin/env python3
"""detect_ai.py - flag AI-writing tells in academic prose.

Baselines are EMPIRICAL, measured from 495 paragraph pairs in which an expert
human academic rewrote LLM-generated marketing/business research prose back into
natural human writing (see references/measured-signals.md). "H" = human target,
"L" = LLM source. The detector scores how far a passage leans toward the LLM end.

Usage:
    python3 detect_ai.py path/to/text.txt
    python3 detect_ai.py            # reads STDIN
    pbpaste | python3 detect_ai.py  # macOS clipboard

It does NOT rewrite. It tells you what to look at. Use the SKILL.md rules to fix.
"""
import sys, re
from collections import Counter

# ---- empirical baselines (per 1,000 words unless noted) ----
BASE = {
    'emdash_per_1k':   {'H': 1.11, 'L': 7.02},   # LLM uses 6.3x more em dashes
    'chars_per_word':  {'H': 6.93, 'L': 7.32},   # LLM uses longer words
    'copula_per_1k':   {'H': 24.2, 'L': 19.1},   # is/are/was/were/be -> human richer
    'semicolon_per_1k':{'H': 1.40, 'L': 1.76},   # weak signal: info only
    'colon_per_1k':    {'H': 3.83, 'L': 4.58},   # weak signal: info only
    'words_per_para':  {'H': 136.0,'L': 53.0},   # LLM over-splits into 2.5x paragraphs
    'sent_len_stdev':  {'H': 12.3, 'L': 10.1},   # human varies rhythm more
    'pct_short_sent':  {'H': 5.6,  'L': 3.3},    # <8 words
    'pct_long_sent':   {'H': 22.1, 'L': 18.4},   # >30 words
}

# Lexical tells: words the LLM over-uses (with z-score from log-odds) -> suggested swap.
# Only content words a writer would actually reconsider are listed (function words excluded).
LEX_TELLS = {
    'additionally': 'also / drop it', 'comprehensive': 'full / detailed / (drop)',
    'notably': '(drop)', 'primarily': 'mainly', 'utilize': 'use', 'utilizing': 'using',
    'utilizes': 'uses', 'employ': 'use', 'employs': 'uses', 'employing': 'using',
    'demonstrates': 'shows', 'demonstrate': 'show', 'demonstrated': 'showed',
    'reveals': 'shows / finds', 'reveal': 'show', 'revealed': 'showed',
    'assess': 'measure / test / look at', 'assesses': 'measures', 'assessing': 'measuring',
    'distinct': 'different / separate', 'diverse': 'different / varied',
    'essential': 'needed / key', 'critical': 'important / key', 'crucial': 'important / key',
    'consistently': '(drop) / always', 'underscore': 'show / stress',
    'underscores': 'shows / stresses', 'underscoring': 'showing',
    'pivotal': 'key / central', 'robust': 'strong / reliable', 'leverage': 'use',
    'leverages': 'uses', 'leveraging': 'using', 'delve': 'go into / look at',
    'foster': 'support / build', 'fostering': 'building', 'enhance': 'improve',
    'enhances': 'improves', 'enhancing': 'improving', 'facilitate': 'help / let',
    'facilitates': 'helps', 'holistic': 'overall', 'seamless': 'smooth',
    'seamlessly': 'smoothly', 'paradigm': 'approach / model', 'realm': 'area',
    'myriad': 'many', 'intricate': 'detailed / complex', 'intricacies': 'details',
    'nuanced': 'subtle', 'interplay': 'interaction', 'navigate': 'handle / deal with',
    'navigating': 'handling', 'establishes': 'sets up', 'presents': 'gives / shows',
    'outlined': 'described / listed', 'throughout': 'across / in',
    'within': 'in', 'among': 'across', 'remains': 'is still / stays',
}

# Phrase tells: regex -> note. Drawn from the LLM-leaning bigrams + curated openers.
PHRASE_TELLS = [
    (r'\bour findings indicate that\b', '"we find that"'),
    (r'\bfindings (?:indicate|suggest|reveal|demonstrate) that\b', '"we find that" / "we show that"'),
    (r'\bthese findings\b', '"this" / name the result'),
    (r'\bthis approach\b', 'name the method'),
    (r'\bour analysis (?:reveals|shows|indicates)\b', '"we find" / "we show"'),
    (r'\bcompared to\b', '"vs" / "than"'),
    (r'\bas a result\b', '"so" / "thus"'),
    (r'\bit is important to (?:note|recognize|understand)\b', 'just say it'),
    (r'\bplays? a (?:crucial|key|pivotal|vital|significant) role\b', '"matters for" / name the effect'),
    (r'\bserves? as\b', '"is"'),
    (r'\bsheds? light on\b', '"shows" / "clarifies"'),
    (r'\bin conclusion\b', '(drop) / "we conclude"'),
    (r'\boverall,\b', '(drop)'),
    (r'\ba wide range of\b', '"many" / be specific'),
    (r'\bunderscores the\b', '"shows the" / "stresses the"'),
    (r'\bdesigned to\b', '"that" + verb'),
    (r'\bin order to\b', '"to"'),
    (r'\bdue to the fact that\b', '"because"'),
    (r'\bwith the goal of\b', '"to"'),
    (r'\bnot only\b.*?\bbut also\b', 'split into plain clauses'),
]

WORD = re.compile(r"[A-Za-z][A-Za-z'\-]+")
COPULA = {'is','are','was','were','be','been','being','am'}

def tok(s): return WORD.findall(s.lower())
def sents(s): return [x for x in re.split(r'(?<=[.!?])\s+', s.strip()) if x.strip()]
def paras(s): return [p for p in re.split(r'\n\s*\n', s.strip()) if p.strip()]

def lean(val, h, l):
    """0 = human-like, 1 = llm-like, clamped, by linear interp between baselines."""
    if l == h: return 0.0
    x = (val - h) / (l - h)
    return max(0.0, min(1.0, x))

def main():
    if len(sys.argv) > 1:
        text = open(sys.argv[1], encoding='utf-8').read()
    else:
        text = sys.stdin.read()
    if not text.strip():
        print('No input text.'); return

    words = tok(text); nw = len(words) or 1
    S = sents(text); P = paras(text)
    slens = [len(tok(s)) for s in S] or [0]
    import statistics as st
    nchars = sum(len(w) for w in words)

    m = {
        'emdash_per_1k': 1000*text.count('—')/nw,
        'chars_per_word': nchars/nw,
        'copula_per_1k': 1000*sum(1 for w in words if w in COPULA)/nw,
        'semicolon_per_1k': 1000*text.count(';')/nw,
        'colon_per_1k': 1000*text.count(':')/nw,
        'words_per_para': nw/max(1,len(P)),
        'sent_len_stdev': st.pstdev(slens) if len(slens)>1 else 0.0,
        'pct_short_sent': 100*sum(1 for x in slens if x<8)/len(slens),
        'pct_long_sent': 100*sum(1 for x in slens if x>30)/len(slens),
    }

    print('='*64)
    print(f'AI-WRITING DETECTOR   ({nw} words, {len(S)} sentences, {len(P)} paragraphs)')
    print('='*64)
    print(f'{"metric":18s} {"value":>8s} {"human":>7s} {"llm":>7s}  lean')
    enough_sent = len(S) >= 12
    # (key, scored?) -- direction is encoded by the baselines themselves
    SPEC = [
        ('emdash_per_1k',  True),          # strongest tell when present
        ('chars_per_word', True),
        ('copula_per_1k',  True),
        ('words_per_para', True),          # over-splitting into short paragraphs
        ('sent_len_stdev', enough_sent),   # rhythm: needs enough sentences
        ('pct_short_sent', enough_sent),
        ('pct_long_sent',  enough_sent),
        ('semicolon_per_1k', False),       # weak: info only
        ('colon_per_1k',   False),         # weak: info only
    ]
    leans = []
    for k, scored in SPEC:
        h, l = BASE[k]['H'], BASE[k]['L']
        ln = lean(m[k], h, l)
        if scored:
            leans.append(ln)
            f = int(round(ln*10))
            bar = '#'*f + '.'*(10-f)
            flag = ' <-LLM' if ln >= 0.6 else ''
            print(f'{k:18s} {m[k]:8.2f} {h:7.2f} {l:7.2f}  {bar}{flag}')
        else:
            tag = 'info' if 'semicolon' in k or 'colon' in k else 'info(<12 sent)'
            print(f'{k:18s} {m[k]:8.2f} {h:7.2f} {l:7.2f}  ({tag})')

    # ---- lexical tells ----
    wc = Counter(words)
    hits = [(w, wc[w], sw) for w, sw in LEX_TELLS.items() if wc[w] > 0]
    hits.sort(key=lambda x: -x[1])
    print('\nLEXICAL TELLS (over-used by LLM)  ->  suggested swap')
    if hits:
        for w, c, sw in hits:
            print(f'  {w:16s} x{c:<3d} -> {sw}')
    else:
        print('  none')
    lex_per_1k = 1000*sum(c for _, c, _ in hits)/nw

    # ---- phrase tells ----
    print('\nPHRASE / CONSTRUCTION TELLS  ->  suggested fix')
    ph_count = 0
    low = text.lower()
    for pat, note in PHRASE_TELLS:
        found = re.findall(pat, low, flags=re.DOTALL)
        if found:
            ph_count += len(found)
            print(f'  [{len(found)}x] /{pat}/  -> {note}')
    if ph_count == 0:
        print('  none')

    # ---- copula-avoidance hint ----
    print()
    if m['copula_per_1k'] < BASE['copula_per_1k']['H']*0.7:
        print('NOTE: low is/are density -> check for copula avoidance '
              '("serves as / represents / constitutes" instead of "is").')

    # ---- overall score ----
    struct = sum(leans)/len(leans) if leans else 0.0
    ph_per_1k = 1000*ph_count/nw
    lex_score = min(1.0, lex_per_1k/20.0)   # ~20 lexical tells/1k words saturates
    ph_score  = min(1.0, ph_per_1k/10.0)    # ~10 phrase tells/1k words saturates
    overall = 100*(0.40*struct + 0.35*lex_score + 0.25*ph_score)
    print('='*64)
    print(f'AI-LIKENESS SCORE: {overall:5.1f}/100   '
          f'(structure {100*struct:.0f}, lexical {100*lex_score:.0f}, phrasing {100*ph_score:.0f})')
    verdict = ('reads human' if overall < 33 else
               'mixed - some tells' if overall < 58 else
               'reads AI - humanize it')
    print(f'VERDICT: {verdict}')
    print('Tip: best signal comes from passages of 150+ words. Use hits above as a checklist.')
    print('='*64)

if __name__ == '__main__':
    main()
