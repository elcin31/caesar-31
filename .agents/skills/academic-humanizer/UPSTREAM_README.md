# humanizer

A Claude Code [skill](https://docs.claude.com/en/docs/claude-code/skills) that
rewrites LLM-generated text into natural human academic prose. Unlike generic
"signs of AI writing" checklists, every rule here is learned from data: 495
paragraph pairs in which an expert academic rewrote LLM drafts of
marketing/business research back into the published human version. The LLM
version is what the skill fixes; the human version is the target.

## What it fixes

Measured differences between the LLM rewrites and the human originals:

| Signal | LLM vs. human | What the skill does |
|---|---|---|
| Em dashes (`—`) | **6.3× more** in LLM | removes them (commas, parentheses, or new sentences) |
| Paragraphs | **2.5× more** splits in LLM | merges over-split paragraphs into dense blocks |
| Latinate verbs | utilize, demonstrate, leverage | swaps for use, show, find, measure |
| Result framing | "our findings indicate that" | rewrites to "we find that" / "Study N shows that" |
| Boosters | comprehensive, robust, crucial | cuts or downgrades; never stacks them |
| Hedge adverbs | notably (6×), additionally (5.4×) | deletes free-floating stance adverbs |
| Copula | LLM avoids "is/are" | restores the plain copula |
| Signposting | "In this section, we examine..." | states it directly |

It also knows what **not** to touch: the rule of three, en dashes,
"thus/thereby", long sentences, and acknowledgments boilerplate are *not* AI
tells in this corpus, so the skill leaves them alone. It restores sentence-length
variety rather than just shortening, because human prose here varies length more
than the LLM does.

## Install

```bash
git clone https://github.com/ashgreat/humanizer.git
cd humanizer
./install.sh            # copies the skill to ~/.claude/skills/humanizer
```

Or copy the files manually into `~/.claude/skills/humanizer/` (user-level) or a
project's `.claude/skills/humanizer/`.

## Use

In any Claude Code session:

> humanize this: *(paste text, or point to a file)*

The skill applies the patterns highest-tier first, preserves every claim,
citation, and number, and returns a final rewrite with no em dashes plus a short
note on what changed.

### Detector

A standalone detector scores how AI-like a passage reads, calibrated on the
corpus (human mean ~22/100, LLM mean ~48/100):

```bash
python3 scripts/detect_ai.py path/to/text.txt
pbpaste | python3 scripts/detect_ai.py    # macOS clipboard
```

It prints per-metric leans, the specific word/phrase hits, and an overall score.
Use it as a checklist, not a verdict. The signal is strongest on passages of 150+
words.

## Contents

```
SKILL.md                              the 28-pattern tiered playbook
scripts/detect_ai.py                  empirically-calibrated AI-likeness detector
references/measured-signals.md        the full quantitative profile
references/before-after-examples.md   annotated real before/after pairs
references/full-taxonomy.md           the complete 28-pattern catalog
```

## How it was built

1. A quantitative pass measured every systematic LLM-vs-human difference (word
   log-odds, bigrams, punctuation, paragraphing, sentence rhythm).
2. A multi-agent analysis read all 495 pairs, extracted ~300 concrete
   before/after transformations, merged them into a taxonomy, and an adversarial
   critic checked the taxonomy against held-out pairs to drop over-claimed rules.
3. The detector was calibrated against the corpus and validated: it scores the
   LLM version higher than its human twin in 86% of pairs.

The example snippets in `references/` are short excerpts from a research corpus,
used to illustrate the transformations.

## License

MIT. See [LICENSE](LICENSE).
