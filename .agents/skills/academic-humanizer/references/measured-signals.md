# Measured signals: LLM rewrite vs. human original

Every number here is measured from **495 paragraph pairs** drawn from 26
academic marketing/business research papers. In each pair, `text` is the real
human-written paragraph from the published paper and `llm_version` is an LLM's
rewrite of that same paragraph. So the **human column is the target** and the
**LLM column is what we want to undo**. "Humanizing" means moving a passage from
the LLM profile back to the human profile.

These are corpus aggregates. On a single short paragraph any one signal can be
absent; look for **clusters**, and weight the strong tells (em dashes,
paragraph-splitting, Latinate verbs, "our findings indicate that") most.

## Aggregate profile (per 1,000 words unless noted)

| Signal | Human | LLM | LLM / Human | Direction |
|---|---|---|---|---|
| Paragraphs per passage | 1.00 | 2.52 | **2.52×** | LLM over-splits |
| Em dashes (—) | 1.11 | 7.02 | **6.30×** | LLM floods them |
| En dashes (–) | 1.07 | 0.65 | 0.60× | human uses *more* (ranges, A–B) |
| Characters per word | 6.93 | 7.32 | 1.06× | LLM picks longer words |
| Copulas (is/are/was/were/be) | 24.2 | 19.1 | 0.79× | LLM avoids "is" |
| Semicolons | 1.40 | 1.76 | 1.26× | weak |
| Colons | 3.83 | 4.58 | 1.20× | weak |
| Words per sentence | 23.1 | 22.7 | ~1.0 | similar |
| Sentence-length std dev | 12.3 | 10.1 | 0.82× | human varies rhythm more |
| Short sentences (<8 words) | 5.6% | 3.3% | 0.59× | human uses more |
| Long sentences (>30 words) | 22.1% | 18.4% | 0.83× | human uses more |

Two takeaways the table makes concrete:

1. **The LLM regresses sentence rhythm toward the mean.** The human writes
   *both* more very-short and more very-long sentences. The LLM clusters around
   mid-length. Restore variety: let some sentences run long, cut others to a
   handful of words.
2. **The LLM inflates word choice and avoids plain "is."** Longer words, fewer
   copulas. Humanizing means shortening words and bringing back "is/are."

## Words the LLM over-uses (z = log-odds, human vs LLM)

Flag these as candidates (function words like *these/both/within/this* are also
over-used but are usually fine to keep). Content-word tells, strongest first:

`additionally` (z 5.2), `findings` (5.1), `primary` (4.8), `comprehensive`
(4.0), `notably` (3.8), `primarily` (3.8), `presents` (3.7), `significant`
(3.7), `established` (3.6), `approach` (3.6), `assess` (3.6), `observed` (3.4),
`reveals` (3.4), `distinct` (3.3), `demonstrates` (3.3), `diverse` (3.2),
`utilizing` (3.1), `practical` (3.1), `utilize` (3.1), `essential` (3.0),
`solely` (3.0), `critical` (3.0), `outlined` (3.0), `consistently` (3.0),
`employ`, `throughout`, `within`, `among`, `remain(s)`.

Curated AI-vocabulary boosters confirmed over-represented here: `crucial`
(6× the human rate), `underscore(s)` (5×), `comprehensive` (4×), `notably`
(6×), `utilize/utilizing` (5–10×), `delve` (0 in human, 4 in LLM),
`enhance/enhancing`, `foster(ing)`, `leverage(ing)`, `robust`, `pivotal`,
`in conclusion` (0 in human).

## Words the human uses far more (the target vocabulary)

`we` (z −7.2), `be` (−5.8), `find` (−5.5), `is` (−5.3), `thus` (−5.2),
`effect` (−5.0), `different` (−4.8), `shows` (−4.5), `because` (−4.1),
`might` (−3.8), `will` (−3.8), `vs` (−3.5, vs LLM "compared to"), `same`,
`change`, `use`, `help`, `good`, `increase`, `used`, `suggests`, `useful`,
`discuss`. Note the possessive forms the LLM strips: `consumers'`,
`customers'`, `retailer's` (apostrophe-s constructions the LLM rewrites into
"of the ...").

## Bigrams: LLM-leaning vs human-leaning

**LLM-leaning** (rewrite away): `such as`, `our findings`, `compared to`,
`our analysis`, `the primary`, `indicate that`, `these findings`,
`this approach`, `we examine`, `demonstrates that`, `as a result`, `refer to`,
`rather than`, `provided in`, `designed to`, `additionally we`, `presented in`,
`to address`, `reveal(s) that`, `underscores the`, `is essential`,
`assess the`, `this study`, `strategies to`.

**Human-leaning** (move toward): `we find`, `find that`, `the effect`,
`effect of`, `we use`, `negative effect`, `the same`, `similar to`,
`to understand`, `an llm`, `in terms of`, `the data`, `how to`, `there is`,
`we also`, `which is`, `shows that`, `show that`, `might be`, `change in`,
`and how`, `and then`.

The pattern is unmistakable: the human states results directly in first person
present (`we find that X`, `we show that X`), names concrete quantities
(`the effect of X on Y`, `negative effect`, `change in`), and uses plain
connectives (`thus`, `so`, `because`). The LLM nominalizes and distances
(`our findings indicate that`, `this approach demonstrates`, `as a result`).

## High-value word swaps (seen in the data)

| LLM | → Human |
|---|---|
| utilize / employ / leverage | use |
| demonstrate(s) / reveal(s) | show(s) / find(s) |
| assess | measure / test / look at |
| comprehensive | full / detailed / (drop) |
| distinct / diverse | different / separate |
| essential / critical / crucial | key / needed / important |
| underscore(s) | show(s) / stress(es) |
| enhance | improve |
| facilitate | help / let |
| numerous / a myriad of | many |
| compared to | vs / than |
| in order to | to |
| our findings indicate that | we find that |
| these findings show | we show that |
| plays a crucial role in | matters for / affects |
| serves as | is |
| as a result | so / thus |
| additionally / moreover | also / (drop and just continue) |
| notably / it is important to note | (drop, just say it) |
| in conclusion / overall | (drop, or "we conclude") |

See `scripts/detect_ai.py` to score a passage against these baselines.
