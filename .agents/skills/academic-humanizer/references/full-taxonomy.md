# Full validated taxonomy (28 patterns, from 296 raw across 495 pairs)

## Latinate verb deflation  [tier: high]
**LLM signature:** Defaults to inflated Latinate verbs for ordinary actions: utilize, employ, leverage, demonstrate, reveal, assess, evaluate, examine, investigate, enhance, facilitate, illustrate, underscore, elucidate, encompass, operationalize, endeavor.
**Human target:** Plain, mostly Anglo-Saxon verbs that carry the same meaning without inflation: use, show, find, test, measure, help, improve, study, highlight, explain, include, spans, try.
**Rule:** Replace inflated Latinate verbs with plain equivalents: utilize/employ/leverage->use; demonstrate->show; reveal->show or find; assess/evaluate->test or measure; examine/investigate->study or look at; enhance->improve or help; facilitate->help; underscore->highlight; elucidate->explain; encompass->include or spans; endeavor->try; operationalize->measure. Quant confirms LLM over-uses utilize (z=3.06), utilizing (z=3.12), employ (z=3.21), assess (z=3.55), reveals (z=3.40), demonstrates (z=3.31); human favors find (z=-5.47), shows (z=-4.49), use (z=-3.20).
**Examples:**
- BEFORE: they demonstrate that LLMs enhance both data generation and analysis
  AFTER : they show that LLMs can assist in both data generation and analysis
- BEFORE: we employed the OpenAI GPT-4 model accessed via API
  AFTER : We use the OpenAI API for the GPT-4 model
- BEFORE: Rather than employing the original similarity metric, we utilize the BERT deep learning approach (Devlin et al., 2018) to assess semantic similarity.
  AFTER : Instead of the original similarity metric, we use the deep learning BERT method (Devlin et al. 2018) to measure semantic similarity
- BEFORE: Our analysis underscores the risks of unethical retail practices
  AFTER : Our analysis highlights the potential for unethical retailing practices

## Distanced result-reporting to first-person 'we find'  [tier: high]
**LLM signature:** Reports results through distancing, nominalized meta-frames that make the findings/analysis the agent: 'our findings indicate/reveal/demonstrate/show that', 'our analysis reveals', 'these findings indicate', 'the research demonstrates', 'our research identifies'.
**Human target:** States the finding directly with a first-person active verb or the study as agent: 'we find that', 'we show', 'Study N shows that', 'the results suggest/show', 'the main takeaway is'.
**Rule:** Replace 'our findings/results/analysis indicate/reveal/demonstrate/show that' with 'we find that', 'we show', or '[Study N] shows that'; keep the authors (or the study) as grammatical agent, not the abstraction. Quant: 'we find' (z=-4.30), 'find that' (z=-3.98), 'shows that' (z=-2.81) strongly human; 'our findings' (z=3.89), 'our analysis' (z=3.51), 'indicate that' (z=3.42), 'reveals that' (z=2.56), 'demonstrates that' (z=3.08) strongly LLM; 'findings' over-used 2x (143 vs 69).
**Examples:**
- BEFORE: Our findings indicate that top competitors exhibit higher 10-K similarity scores than more distant competitors
  AFTER : We find that top competitors have higher 10-K similarity than other (distant) competitors
- BEFORE: The research reveals that displaying even a single like dramatically increases users' willingness to like and click on an ad.
  AFTER : They find that displaying the first like can significantly increase users' tendencies to both like and click on an ad.
- BEFORE: Findings from Study 1 indicate that, in addition to variations in food supply, differences in preferences can also shape the dietary choices
  AFTER : Study 1 shows that, over and above differences in supply, differences in preferences may also influence the dietary choices
- BEFORE: Our analysis reveals that consumer spending is positively and significantly correlated
  AFTER : We find that consumer spending has positive and significant yet subtle correlations

## Hedge/booster adverb removal  [tier: high]
**LLM signature:** Sprinkles free-floating stance adverbs, often sentence-initially, to signal emphasis or transition: Notably, Importantly, Additionally, Specifically, Particularly, Significantly, Consistently, Primarily, Clearly, Evidently, Ultimately, Fundamentally, Essentially, Subsequently, Consequently.
**Human target:** Deletes the adverb entirely and lets the evidence carry the emphasis; if flagging is truly needed, recasts as a short clause ('Note that', 'It is worth noting that') or uses a single precise word.
**Rule:** Delete sentence-opening or mid-sentence booster/hedge adverbs unless they quantify a precise degree; replace 'subsequently'->'then', 'additionally'->'also'. Keep 'Importantly'/'Critically' only when emphasis is genuinely warranted. Quant: LLM over-uses additionally (z=5.15, 59 vs 11), notably (z=3.81, 31 vs 5), primarily (z=4.81), primarily (z=3.75), consistently (z=2.96), significant (z=3.65); 'additionally' is 5.4x and 'notably' 6.2x.
**Examples:**
- BEFORE: Notably, LLM-generated data often match or surpass human-generated data in terms of depth and insightfulness.
  AFTER : LLM-generated data are as good as and sometimes better than human-generated data on dimensions such as depth and insightfulness.
- BEFORE: the human–LLM hybrid consistently outperforms either approach used in isolation
  AFTER : the human–LLM hybrid outperforms its human-only or LLM-only counterpart
- BEFORE: Notably, the strongest negative effects are observed in categories such as Local Services, Hair Removal, and Health.
  AFTER : Among the categories with strong negative effects are Local Services, Hair Removal, and Health
- BEFORE: Importantly, our findings demonstrate that the cumulative history of app crashes, not just isolated incidents, plays a crucial role in shaping user engagement.
  AFTER : Our analyses reveal that the entire history of prior app crashes influences consumer engagement

## Inflated adjective/booster deflation  [tier: high]
**LLM signature:** Pads nouns with heavy evaluative adjectives: comprehensive, robust, crucial, critical, essential, significant, substantial, pivotal, vital, indispensable, compelling, profound, multifaceted, novel, innovative, invaluable, seamless, distinctive, pioneering.
**Human target:** Drops the booster or downgrades to a plain, modest, specific qualifier: detailed, key, important, strong, broad, useful, novel, first; never stacks boosters.
**Rule:** Cut or downgrade boosters: comprehensive->detailed/broad (or cut); crucial/essential/vital->key/important; robust->strong; compelling evidence->strong evidence; multifaceted->various; pivotal/indispensable->important; pioneering->first; substantial->drop. Never stack a booster with 'significant'. Quant: LLM over-uses comprehensive (z=4.04, 38 vs 8; 4.1x by per-1k), significant (1.954 vs 1.189/1k), essential (z=3.04), critical (z=2.98), crucial (0.271 vs 0.045/1k).
**Examples:**
- BEFORE: Study 4 offered comprehensive support for our full model. Our findings demonstrated that BNPL installment payments lowered perceived costs and enhanced budget management
  AFTER : Study 4 provided evidence for our full model. We showed that BNPL installment payments reduced perceived costs and facilitated budget control
- BEFORE: Study 1 offers compelling evidence supporting the hypothesized negative impact of company size on word-of-mouth (WOM) valence. This effect proves robust and generalizable
  AFTER : Study 1 provides strong evidence for the proposed negative effect of company size on WOM valence. This effect is robust and generalizable
- BEFORE: we propose a comprehensive research agenda aimed at exploring the multifaceted dimensions of the enrichment economy.
  AFTER : we propose a research agenda that addresses the various aspects of the enrichment economy.

## Em-dash aside removal  [tier: high]
**LLM signature:** Uses em-dash parentheticals (single or paired) to insert definitions, restatements, qualifications, examples, or glosses mid-sentence: '—rather than taste—', '—a notion we explored empirically—', '—specifically those involving...—', '—including retailers, policymakers, and consumers—'.
**Human target:** Integrates the aside into the main clause with commas or prepositions, rewrites it as a main-clause verb, splits it into a separate sentence, or uses ordinary parentheses with 'i.e.,'/'e.g.,'; reserves em-dashes for genuinely pivotal interruptions.
**Rule:** Remove em-dash asides: fold into the main clause as a relative or comma-set clause, rewrite as a main-clause verb, move into parentheses '(i.e., ...)'/'(e.g., ...)', or split into a separate sentence; never stack paired dashes to cram qualifications into one sentence. Quant: em-dash is the single strongest tell at 6.30x (7.019 vs 1.114 per 1k); en-dash, by contrast, is human-leaning (0.60x).
**Examples:**
- BEFORE: the marketing research industry, in particular, stands on the verge of disruption fueled by LLM-driven innovation—a notion we explored empirically in this study
  AFTER : We believe that the marketing research industry is also poised for disruption because of innovations in LLMs and investigate this claim empirically.
- BEFORE: fillingness—rather than taste—serve as the crucial SES differentiator, accounting for the diminished appeal of healthy foods
  AFTER : fillingness, rather than taste, is a key SES differentiator, explaining why low-income individuals are less attracted to healthy food items
- BEFORE: company size influences consumers' propensity to share WOM depending on the quality of their experiences—in other words, whether or not they choose to communicate their feedback
  AFTER : company size impacts consumers' likelihood to share WOM as a function of experience quality (i.e., they decide whether or not to share)
- BEFORE: Rather than indiscriminately including all possible interactions—which is infeasible—we adopted a pragmatic approach.
  AFTER : Instead of blindly or exhaustively including interaction terms, which is doomed to fail, we took a practical approach.

## Paragraph consolidation (merge LLM splits)  [tier: high]
**LLM signature:** Splits a continuous argument, method thread, or single example into multiple short paragraphs, one idea each, often with a signpost opener (Next, Furthermore, Finally), creating white space and a listy feel.
**Human target:** Consolidates logically continuous content into one dense, flowing paragraph, using internal connectives (next, also, moreover, specifically) instead of paragraph breaks; reserves breaks for genuine topic shifts.
**Rule:** Merge consecutive paragraphs that develop a single train of thought into one block; demote paragraph breaks to sentence-level connectives; collapse enumerated points under one heading into one paragraph. Quant: LLM produces 2.52x the paragraphs per doc (2.515 vs 1.000) at near-identical word count, so each LLM paragraph is roughly 2.5x shorter.
**Examples:**
- BEFORE: Study 2 offered causal evidence that BNPL installment payments led to higher spending compared to an equivalent lump sum payment. Notably, this increase in spending was driven by differences in perceived financial constraints...

Importantly, neither payment method accrued interest...
  AFTER : Study 2 provided causal evidence that BNPL installment payments increased spending compared with an equivalent lump sum payment. Moreover, differences in perceived financial constraints explained the effect of BNPL installment payments on spending. Specifically, participants who paid in installments (vs. lump sum) felt less financially constrained and spent more. In this experiment, both payment methods did not incur any interest...
- BEFORE: The fourth research phase shifted focus to the perspective of B2B buyers. We conducted ten in-depth interviews with senior buyers...

In the fifth and final phase, we carried out seven in-depth interviews with sales executives at supplier firms identified by buyers as industry visionaries.
  AFTER : Next, the fourth phase focused on the B2B buyer's perspective and comprised ten in-depth interviews with senior B2B buyers from various markets and industries. … Finally, the fifth phase comprised seven in-depth interviews with sales executives at suppliers identified by buyers as particularly visionary.

## Signpost / roadmap / meta-announcement removal  [tier: high]
**LLM signature:** Adds free-standing road-map or meta-structure sentences that announce what the text will do: 'In this section, we examine...', 'In the following section, we describe...', 'Building on these findings, our next objective is to...', 'The findings are organized into two primary sections', 'This research offers valuable insights for...'.
**Human target:** Drops the signpost, folds it into the substantive opening sentence, or compresses a multi-sentence preview into one lean sentence using numbered markers (First, Second, Third).
**Rule:** Delete or compress free-standing 'In this section, we...' / 'Building on X, our next objective is...' previews; integrate essential framing into the first content sentence or a brief transition ('We next describe...'); compress multi-sentence roadmaps into one sentence. Quant: 'we examine' (z=3.21) and 'this study' (z=2.33) are LLM-leaning bigrams; 'next' (z=-3.55) is human-leaning.
**Examples:**
- BEFORE: To address this limitation, we outline three methods for incorporating domain expertise into large language models: few-shot learning, retrieval-augmented generation (RAG), and fine-tuning.
  AFTER : We next describe three approaches to inject domain knowledge for an LLM: few-shot learning, RAG, and fine-tuning.
- BEFORE: In the following section, we examine the effects of app crashes in greater detail.
  AFTER : Next, we discuss the impact of app crashes in detail.
- BEFORE: Study 2b offers a closer examination of the fillingness attribute. It explores why this characteristic may hold particular significance for consumers with low socioeconomic status (SES).
  AFTER : Study 2b dives deeper into the fillingness attribute. Specifically, it examines the reasons why fillingness might be particularly important for low-SES consumers.
- BEFORE: This research offers valuable insights for policy makers in shaping effective environmental and socioeconomic regulations.
  AFTER : This research is also valuable to policy makers in designing environmental and socioeconomic regulations.

## Nominalization to verb  [tier: medium]
**LLM signature:** Buries actions in noun-phrase shells and participial result clauses: 'the implementation of', 'the elimination of', 'conduct an investigation of', 'provide a summary of', 'the occurrence of exact zero values', 'ensure the robustness of', 'indicating that multicollinearity does not pose an issue'.
**Human target:** Restores the finite verb or a tight noun compound: 'implement', 'end', 'investigate', 'summarize', 'the presence of', 'check', 'so multicollinearity is not a concern'.
**Rule:** Unpack nominalizations into finite verbs and drop the governing noun shell: 'conduct an evaluation of'->'evaluate'; 'provide a summary of'->'summarize'; 'the elimination of X'->'end X'; 'ensure the robustness of'->'check'; replace '-ing' result clauses ('indicating that X does not pose an issue') with coordinated main clauses ('so X is not a concern').
**Examples:**
- BEFORE: films featuring a predominantly Black cast exhibit a greater disparity between average audience and critic ratings.
  AFTER : the deviation between average audience and critic ratings increases for movies with a more predominantly Black cast.
- BEFORE: variance inflation factors (VIFs) remain well below the recommended threshold of 10 (Hair et al., 2017), indicating that multicollinearity does not pose an issue.
  AFTER : The VIFs in the four estimated models are well below the recommended threshold of 10 (Hair et al. 2017), so multicollinearity is not a concern.
- BEFORE: they do underscore the importance of eliminating biannual time changes
  AFTER : Our results suggest that policy makers should continue trying to end the time changes

## Passive / noun-subject to active first-person  [tier: medium]
**LLM signature:** Uses agent-less passives or impersonal noun-phrase subjects to avoid naming the researcher: 'respondents were assigned', 'surveys were administered', 'A comprehensive account is provided in', 'The validity is strengthened by three experiments', 'is achieved through the use of'.
**Human target:** Restores first-person active voice or names the actor: 'we recruited', 'we distributed', 'details can be found in', 'three experiments support', 'shown in'.
**Rule:** Convert agent-less passives and impersonal noun-subjects to active voice with the logical subject (usually 'we', or the experiment/table) as grammatical subject; 'a detailed account is provided in X'->'details can be found in X' or 'X provides details'; 'shown in' not 'provided in'. Quant: 'we' strongly human (z=-7.19, 793 vs 525); 'be'/'is' human-leaning (copula); 'provided in' (z=2.83) and 'presented in' (z=2.68) are LLM bigrams.
**Examples:**
- BEFORE: Eligibility criteria required participants to be located in the United States, at least 18 years old, and possess a high school diploma or higher.
  AFTER : we recruited 250 participants on Prolific in November 2024 using these screening criteria: Respondents are located in the United States, are over 18 years of age, and have a high school diploma or higher education.
- BEFORE: The validity and generalizability of these insights are strengthened by three controlled experiments, in which app crashes were exogenously introduced in an alternative context.
  AFTER : Three experiments in which crashes are exogenously manipulated in a different context support the validity and generalizability of these findings
- BEFORE: In March 2017, we administered surveys to retailers ... A total of 2,856 survey invitations were sent out
  AFTER : We distributed the surveys in March 2017 ... In total, we sent 2,856 survey invitations via email

## Copula restoration  [tier: medium]
**LLM signature:** Avoids plain 'is/are' by recasting with heavier verbs: 'hinges on', 'is predicated on', 'is contingent upon', 'arises because', 'represents', 'constitutes', 'is characterized by', 'serves as'.
**Human target:** Restores plain 'is/are', 'depends on', or 'refers to'.
**Rule:** Replace elaborate verbal phrases with the copula or a plain verb: 'hinges on'/'is predicated on'/'is contingent upon'->'depends on'; 'is represented by'/'is characterized by'/'constitutes'->'is'; 'serves as'->'is'. Quant strongly supports this: human over-uses 'be' (z=-5.84) and 'is' (z=-5.28); 'to be' (z=-4.12), 'there is' (z=-2.96), 'that is' (z=-2.89), 'which is' (z=-2.86) all human-leaning.
**Examples:**
- BEFORE: The success of zero-shot prediction hinges on the quality and clarity of the prompts provided.
  AFTER : The effectiveness of zero-shot prediction depends on the quality of prompts.
- BEFORE: Archetype prevalence is represented by the parameter estimate (νc), which is empirically nearly equivalent to the percentage of campaigns assigned to each archetype.
  AFTER : The archetype prevalence is the parameter estimate of (νc), which empirically is almost the same as the percent of campaigns assigned to each archetype.

## 'compared to' / spelled-out comparison to '(vs.)' shorthand  [tier: medium]
**LLM signature:** Spells out comparisons in full prose: 'compared to those with higher status', 'rather than debit cards', 'are more likely than X to', 'consumers with lower socioeconomic status, compared to those with higher status'.
**Human target:** Uses compact parenthetical shorthand '(vs. X)' and 'than'; states comparisons probabilistically with the focal subject first.
**Rule:** Replace 'compared to' with 'than' or fold into '(vs. X)' parentheticals; 'consumers with lower X, compared to those with higher X'->'low- (vs. high-) X'; 'are more likely than X to [verb]'->'compared with X, [subject] tend to [verb]'. Quant is decisive: 'compared to' is almost purely LLM (z=3.55, 36 vs 1), while 'vs' is almost purely human (z=-3.47, 34 vs 1).
**Examples:**
- BEFORE: the rise in spending is especially pronounced among customers who previously made smaller purchases and those who depended more on credit rather than debit cards prior to adopting BNPL
  AFTER : this increase in spending is greater for smaller- (vs. larger-) basket shoppers and for shoppers who relied more heavily on credit (vs. debit) cards before adoption
- BEFORE: the findings reveal that consumers with lower socioeconomic status, compared to those with higher status, are (a) more likely to select unhealthy foods
  AFTER : show that low- (vs. high-) socioeconomic-status consumers are more likely to (a) choose unhealthy items

## Section heading simplification (sentence case, drop gerunds)  [tier: medium]
**LLM signature:** Verbose, gerund-heavy, title-case headings, often with a colon-subtitle: 'Enhancing Predictions with Context: Advancing Beyond Zero-Shot Approaches', 'Study 5: Examining Moderating Effects', 'Differentiating HS from Traditional B2B Selling Approaches'.
**Human target:** Shorter headings in sentence case, key noun first, plain noun or imperative-verb forms: 'Study 5: Moderating Effects', 'Coding of thought listing', 'Distinguishing HS from Existing B2B Selling Paradigms'.
**Rule:** Shorten headings: strip gerund-action words (Enhancing, Examining, Assessing, Crafting) to plain noun or imperative forms; apply sentence case (capitalize only the first word and proper nouns); put the key noun first; prefer 'Effect of X on Y' over 'Impact of X on Y'; 'Traditional'->'Existing'.
**Examples:**
- BEFORE: Study 5: Examining Moderating Effects
  AFTER : Study 5: Moderating Effects
- BEFORE: Enhancing Predictions with Context: Advancing Beyond Zero-Shot Approaches
  AFTER : Incorporating Context: Improving Beyond Zero-Shot Predictions
- BEFORE: Step 5: Crafting the Paper
  AFTER : Step 5: Write the Paper

## Formal connective downgrading  [tier: medium]
**LLM signature:** Opens sentences with heavy formal connectives: Additionally, Furthermore, Moreover, Consequently, Nonetheless, Conversely, In contrast.
**Human target:** Uses lighter, plainer connectives or restructures: Also, Thus, Further, Yet, But, In addition, However, Instead, Finally; or embeds the link and starts with the subject.
**Rule:** Replace heavy sentence-initial connectives (Additionally->In addition/Also; Furthermore/Moreover->Further/Also; Consequently->Thus; Conversely/In contrast->Yet/But/Instead) or restructure to start with the subject. Quant: 'additionally' is a top LLM tell (z=5.15, 59 vs 11; 0.887 vs 0.163/1k) and 'additionally we' (z=2.79) a top bigram; human over-uses 'thus' (z=-5.15), 'then' (z=-3.50), 'because' (z=-4.07).
**Examples:**
- BEFORE: Additionally, participants in our panel reported snacking approximately 1.4 times per day, indicating that daily analysis is suitable and robust for Study 1.
  AFTER : Further, consumers in the panel snacked about 1.4 times per day, which suggests that individuals tend to snack more than once a day. Thus, day-level analysis is appropriate for Study 1.
- BEFORE: Moreover, with respect to brand metrics, efficiency and inefficiency appear to be approximately normally distributed
  AFTER : Furthermore, efficiency/inefficiency with respect to brand metrics appears to be approximately normally distributed

## Summary / conclusion-frame removal  [tier: medium]
**LLM signature:** Closes sections with explicit summary-frame words plus restatement or self-praise: 'In summary,', 'Collectively,', 'Taken together,', 'In conclusion, this pioneering study sheds new light on...', 'It is hoped that...', 'These results provide clear evidence in support of'.
**Human target:** Omits the summary frame or folds its content into the final substantive sentence; opens with 'To conclude,' or 'In sum,' + a direct factual statement; replaces self-praise with plain claims; 'It is hoped that'->'Hopefully'.
**Rule:** Remove 'In summary,'/'Collectively,' meta-closings and state the synthesis directly or with a single integrating sentence ('Taken together,'); replace self-praising framing ('pioneering', 'sheds new light') with plain factual statements; 'These results provide clear evidence in support of X'->'This finding provides supporting evidence for X'; 'It is hoped that'->'Hopefully'. Quant: 'in conclusion' is LLM-only (0/4).
**Examples:**
- BEFORE: In summary, this pioneering study on the role of marketing in the context of import competition sheds new light on its importance for incumbent firm performance. It is hoped that these findings will inspire further scholarly work in this critical area.
  AFTER : To conclude, the findings of this first study on the role of marketing in the face of import competition provide novel insights into the relevance of marketing for incumbent firm performance. Hopefully, this study stimulates additional work in this area.
- BEFORE: In summary, the interplay produces two divergent outcomes: increased conformity in liking driven by both informational and normative influence, and a crowding-out of informational value in clicking due to normatively driven social cues.
  AFTER : Taken together, the enhanced conformity effect on liking and the crowding-out effect on clicking can explain the divergent pattern of liking and clicking observed in Figure 3.

## 'It is important to note' / meta-commentary removal  [tier: medium]
**LLM signature:** Flags otherwise-direct statements with explicit meta-commentary: 'It is important to note that', 'It is important to recognize that', 'It is worth noting that', preceding a plain claim.
**Human target:** Drops the flag and states the point directly, or uses a bare 'Note that'.
**Rule:** Delete 'It is important to note/recognize that'; if flagging is truly needed, use bare 'Note that'. Quant: 'it is important' is LLM-leaning (0.135 vs 0.045/1k, 9 vs 3).
**Examples:**
- BEFORE: It is important to note that all firms engaging in community-building on Twitter also use the platform to share content
  AFTER : Note that all the firms that use Twitter to create communities also use Twitter for sharing content
- BEFORE: It is important to note that a crowding-out effect may also occur with the liking response. However, our central assumption is that liking is primarily influenced by normative social influence.
  AFTER : Note that it is possible that the crowding-out effect also exists for the liking response. However, our key assumption is that liking is more driven by normative social influence.

## Abstract framing-wrapper / throat-clearing removal  [tier: medium]
**LLM signature:** Wraps statements in abstract framing or transitional throat-clearing that restates prior logic: 'Drawing from insights gained in Study 2...', 'Against this backdrop', 'In light of this', 'Guided by this rationale', 'Building on these findings,', 'Having established these preliminary insights, we now proceed to'.
**Human target:** States the content directly; if a transition is needed, uses a concrete phrase ('Based on X', 'Given X', 'We next turn to').
**Rule:** Cut abstract framing clauses ('Drawing from X', 'Against this backdrop', 'In light of this', 'Guided by this rationale') and state the point directly; replace participial/padded openers ('Having established X, we now proceed to Y')->'We next turn to Y'.
**Examples:**
- BEFORE: Building on these findings, our subsequent studies explore how the desire for satiety influences food selection
  AFTER : Our next studies demonstrate how fillingness considerations shape food choices
- BEFORE: Having established these preliminary insights, we now proceed to the formal set of studies designed to test our proposed hypotheses.
  AFTER : We next turn to the formal set of studies to test our proposed hypotheses.
- BEFORE: Drawing from insights gained in Study 2 as well as the evolving landscape of marketing survey research, we present a roadmap
  AFTER : Based on the lessons learned from Study 2 and the broader landscape of survey research in marketing, we end with a road map

## Compress long compound sentences into short declaratives  [tier: medium]
**LLM signature:** Packs multiple qualifications, results, and contrasts into one long compound-complex sentence using semicolons, em-dashes, and stacked subordinate clauses; buries the main claim inside a framing clause.
**Human target:** Splits into two or three short declarative sentences, each with one main claim, leading with the claim; sequences as cite-table -> state-finding -> make-comparison.
**Rule:** Break compound sentences that embed results, contrasts, and qualifications into separate short sentences; state the main claim first, then the qualification as a follow-on. Quant: human sentence-length stdev is higher (12.3 vs 10.1) and humans use more long (>30w: 22.1% vs 18.4%) AND more short (<8w: 5.6% vs 3.3%) sentences — i.e., greater rhythm variance, not uniformly shorter sentences.
**Examples:**
- BEFORE: The results, presented in Columns 4 and 5 of Table 2, reveal a distinctly different pattern: approximately 80% of campaigns achieve scores in the two highest reach-efficiency bands, in stark contrast to only 8% reaching the top bands for lift efficiency.
  AFTER : Columns 4 and 5 of Table 2 show these results. This second frontier shows a markedly different pattern. With respect to reach, 80% of campaigns fall near the two highest reach-efficiency scores. This is compared with 8% of campaigns in the two highest efficiency bands for lift.
- BEFORE: This study addresses a key gap in task pursuit research by focusing on app crashes—a distinct form of interruption that is negatively valenced, occurs frequently, and is typically followed by a rapid recovery
  AFTER : This study bridges a gap in task pursuit research by examining app crashes, a distinct type of interruptions characterized by negative (as opposed to neutral) valence, swift recovery, and frequent occurrence

## Hypothesis / proposition phrasing normalization  [tier: medium]
**LLM signature:** States hypotheses with 'All else being equal', inflated causal verbs ('negatively impacts', 'has a greater influence on X compared to Y'), 'stronger/weaker' magnitude, 'described in HXa', and 'hypothesized/anticipated that'; bolds labels (**H1:**).
**Human target:** Uses 'Holding everything else equal', plain effect language with a copula ('has a negative effect on'), 'than'/'(vs.)' comparisons, 'more/less pronounced', bare 'in HXa', 'We hypothesized/reasoned that', focal subject first, no bold labels.
**Rule:** 'All else being equal'->'Holding everything else equal'; 'negatively/positively impacts'->'has a negative/positive effect on'; 'greater influence on X compared to Y'->'stronger for X than Y'; 'stronger/weaker'->'more/less pronounced'; drop 'described' before 'in HXa'; 'hypothesized/anticipated that'->'reasoned that'/'expected'; open hypotheses with the focal subject; remove markdown bold from labels. Quant: 'effect' (z=-5.00) and 'negative effect' (z=-3.22) strongly human; 'influence of'/'the influence' LLM-leaning bigrams.
**Examples:**
- BEFORE: H1: Larger company size negatively impacts overall WOM valence.
  AFTER : H1: Company size has a negative effect on aggregate WOM valence.
- BEFORE: H2: Daylight saving time has a greater influence on consumers' unhealthy behaviors in the evening compared to daytime hours.
  AFTER : H2: The impact of daylight saving time on consumers' unhealthy behavior is stronger in the evening than in daytime hours.
- BEFORE: The attenuation effect described in H4a is stronger when the critics are White and weaker when the critics are Black.
  AFTER : The attenuation effect in H4a is more pronounced when critics are White and less pronounced when critics are Black.

## Strong declaratives to evidence-matched hedges  [tier: medium]
**LLM signature:** Over-claims relative to observational evidence: 'reveals that', 'demonstrates that', 'underscores the need for', 'it is crucial that X must', 'is essential'.
**Human target:** Downgrades to measured hedges matched to the evidence: 'suggests that', 'implies that', 'should', 'it is in the interest of', 'may benefit from'.
**Rule:** Match epistemic strength to evidence: replace reveal/demonstrate/underscore-the-need/is-crucial with suggest/imply/should/may when conclusions are inferred from observational data. Quant: human over-uses 'suggests' (z=-2.76), 'might' (z=-3.84), 'will' (z=-3.79), 'can' (z=-3.30); LLM over-uses 'underscores the' (z=2.56), 'is essential' (z=2.36).
**Examples:**
- BEFORE: Collectively, these findings underscore the need for policymakers and businesses to offer greater support to consumers during the onset of daylight saving time.
  AFTER : Overall, the findings imply that public policy makers and businesses should find ways to support consumers around the onset of daylight saving time.
- BEFORE: it is crucial for crowdfunding platforms to identify additional drivers of racial inequity in donation outcomes.
  AFTER : it is in the interest of donation-based crowdfunding platforms to understand other sources of racial inequity in donation amounts.

## Historical present tense for study procedures  [tier: low]
**LLM signature:** Narrates the paper's own study procedures in simple past: 'we performed', 'we collected', 'we conducted', 'we leveraged', 'were analyzed', 'were asked'.
**Human target:** Uses historical present for procedures conducted as part of the study: 'we conduct', 'we extract', 'we ask', 'is analyzed', 'are asked'.
**Rule:** Switch narrative study-procedure verbs from simple past to historical present ('we leveraged'->'we ask/use'; 'were analyzed'->'is analyzed'; 'we performed'->'we conduct'). Completed-work summaries in the discussion can instead take present perfect ('we have investigated').
**Examples:**
- BEFORE: Before proceeding with empirical tests of our hypotheses, we performed a preliminary study focused on analyzing semantic information from Twitter (now X).
  AFTER : Before empirically testing our hypotheses, we conduct a preliminary study that involves an analysis of semantic information from Twitter (now X).
- BEFORE: Rather than directly replicating respondent profiles from the original study, we leveraged the LLM to recommend a diverse group of potential participants
  AFTER : Instead of replicating the respondent profiles in the original study, we ask the LLM to suggest a group of respondents to generate ideas for this qualitative research

## Figure/table reference verb choice  [tier: low]
**LLM signature:** Introduces figures and tables with 'presents', 'illustrates', 'displays', 'provides', or elaborate multi-clause notes: 'Figure 6 presents a comparison', 'This figure presents plots illustrating the model's estimated effects...'.
**Human target:** Uses 'reports', 'shows', 'summarizes', or 'compares' with direct, minimal note prose; matches the target author's house verb (some prefer reports/shows, some prefer presents over displays).
**Rule:** Per-author figure verbs: replace presents/illustrates/provides->reports/shows/summarizes/compares where the human prefers it; replace displays->presents where the human prefers it; match the target author's house verb rather than defaulting to 'presents'. Quant: LLM over-uses 'presents' (z=3.66, 38 vs 11), 'presented' (z=3.04), 'presented in' (z=2.68); human over-uses 'shows' (z=-4.49) and 'shows the'/'shows that' bigrams.
**Examples:**
- BEFORE: Figure 6 presents a comparison between the actual data and the synthetic measures for various attitudes
  AFTER : Figure 6 reports how the synthetic measures for a variety of attitudes, measured on a five-point scale, compare with the actual data.
- BEFORE: This figure presents plots illustrating the model's estimated effects of social influence on likes and clicks, shown in relation to the number of social cues.
  AFTER : This figure shows the plots of the model estimates of the effects of social influence on likes and clicks as a function of the number of social cues.

## Cross-reference and citation formatting normalization  [tier: low]
**LLM signature:** Passive cross-references and elevated reader-direction: 'Additional details can be found in', 'For additional details, refer to', 'as demonstrated by', 'of the Web Appendix'; cites with ampersand+comma '(Small & Verrochi, 2009)'.
**Human target:** Direct active or imperative reference: 'See X for details', 'X provides details', 'shown in', 'in the Web Appendix'; cites with 'and' and no comma '(Small and Verrochi 2009)'.
**Rule:** Replace 'refer to'->'see'; 'details can be found in X'->'See X for details' or 'X provides details'; 'as demonstrated by'->plain parenthetical; 'of the Web Appendix'->'in the Web Appendix'; inside citations use 'and' not '&' and drop the comma before the year; move appendix/figure references into parentheses within the same sentence. Quant: 'refer' (z=2.91) and 'refer to' (z=3.06) are LLM tells.
**Examples:**
- BEFORE: For additional details, refer to the Web Appendix.
  AFTER : See the Web Appendix for details.
- BEFORE: Table 8 provides an overview of these tests, including their motivations and key findings, while detailed analyses are presented in Web Appendixes H through K.
  AFTER : We summarize the tests, the reasons behind the tests, and key results in Table 8 (the detailed analyses appear in the Web Appendixes H through K).

## Acknowledgments-formula simplification  [tier: low]
**LLM signature:** Florid, emotive, multi-sentence acknowledgments: 'We gratefully acknowledge', 'extend their heartfelt gratitude/appreciation', 'We are indebted to', 'pivotal contributions', 'for their valuable feedback on earlier drafts', 'Special thanks are due to X for outstanding Y', 'Any errors remain the sole responsibility of the authors'.
**Human target:** Plain 'We thank' / 'would like to thank' throughout, consolidated into one semicolon-separated sentence: 'useful/helpful feedback on previous versions', 'excellent' not 'outstanding', 'All errors are our own'; 'invaluable' reserved for named individuals.
**Rule:** Replace 'gratefully acknowledge'/'are indebted to'/'extend heartfelt gratitude'/'appreciate'->'thank' (or 'would like to thank'); 'valuable feedback on earlier drafts'->'useful/helpful feedback on previous versions'; 'outstanding'->'excellent'; 'Any errors remain the sole responsibility of the authors'->'All errors are our own'; consolidate thanked groups into one sentence with 'as well as'.
**Examples:**
- BEFORE: The author gratefully acknowledges Len Berry... for their valuable feedback on earlier drafts of this article. Special thanks are also due to Ralph Park for his outstanding proofreading of the manuscript.
  AFTER : The author would like to thank Len Berry... for useful feedback on previous versions of the article. The author would like to thank Ralph Park for excellent proofreading assistance on the manuscript.
- BEFORE: We are grateful to the anonymous data providers whose contributions made this study possible. Any errors remain the sole responsibility of the authors.
  AFTER : The authors thank anonymous data providers for sharing the data used in the study. All errors are our own.

## Quote-framing reduction  [tier: low]
**LLM signature:** Surrounds a quotation with multiple paraphrase sentences and editorializing meta-commentary ('encapsulates this ethos', 'underscores the power of', 'highlights the company's dedication to'), often with long past-tense attribution ('who shared:').
**Human target:** Introduces the quote briefly with a plain present-tense verb ('As X explains:', 'X notes'), lets it stand, then adds one focused analytical sentence; cuts pre-quote paraphrase and post-quote restatement.
**Rule:** Introduce quotations with plain attribution verbs (explains, notes, says, is evident from) rather than editorializing framing; after a block quote, write one or two focused sentences linking it to the argument and cut duplicative restatement; avoid past-tense 'shared/observed'.
**Examples:**
- BEFORE: This shift is encapsulated by a chief purchasing officer from the machinery industry, who shared:
  AFTER : This is evident from the following quote from a chief purchasing officer in the machinery industry:
- BEFORE: Eric Barela, Salesforce's Director of Measurement and Evaluation, highlights the company's dedication to measuring the tangible value of its innovations.
  AFTER : Eric Barela, Salesforce's director of measurement and evaluation, underscores the company's commitment to tracking the impact of these innovations to ensure they deliver value to customers.

## Markdown / formatting normalization  [tier: low]
**LLM signature:** Adds bold hypothesis labels (**H1:**), blank lines between heading and body, and blank-line separation between consecutive hypotheses.
**Human target:** Plain inline text: no bold labels, heading run together with the first body sentence, hypotheses run as sequential inline text.
**Rule:** Remove markdown bold from hypothesis labels; collapse line breaks between consecutive hypotheses; remove blank lines between a section heading and the following paragraph (run them together).
**Examples:**
- BEFORE: **H1:** Strong brands are more likely to employ individual incentives, whereas weak brands are more inclined to use group incentives.

**H2:** Group incentives are more likely than individual incentives to adopt a quota-based plan
  AFTER : H1: Strong brands are more likely to use individual incentives than weak brands, while weak brands are more likely to use group incentives than strong brands. H2: Group incentives are more likely than individual incentives to follow a quota plan
- BEFORE: Discussion

Findings from Studies 1a and 1b offer consistent evidence
  AFTER : Discussion The results of Studies 1a and 1b provided convergent evidence

## 'thereby/therefore' chained-conclusion removal  [tier: low]
**LLM signature:** Chains conclusions with 'thereby + gerund' or 'subsequently': 'thereby supporting H3', 'thereby enhancing the practical relevance', 'which subsequently alleviated'.
**Human target:** States the consequence as a bare participle, a new clause, or with 'thereby'/'which in turn' only where it tightens a genuine causal chain: 'supporting H3', 'In other words, ...'.
**Rule:** Remove decorative 'thereby + gerund' endings; place the consequence in a new main clause ('In other words, ...') or append the bare participle ('supporting H3' not 'thereby supporting H3'); use 'thereby'/'which in turn' only to compress a real causal chain.
**Examples:**
- BEFORE: In summary, our findings reveal that greater affective expression in campaign descriptions substantially reduces the disparity…, thereby supporting H3.
  AFTER : In other words, we find that when the campaign description expresses more affective cues, the differential impact…is reduced significantly, supporting H3.
- BEFORE: BNPL installment payments lowered perceived costs and enhanced budget management, which subsequently alleviated perceived financial constraints and increased the likelihood of purchase.
  AFTER : BNPL installment payments reduced perceived costs and facilitated budget control, thereby reducing perceived financial constraints, which in turn, increased purchase likelihood.

## Direct rhetorical questions for research questions / future research  [tier: low]
**LLM signature:** Frames research questions through a meta-sentence with a colon ('This raises a key question: how can X...?') or converts them into noun-clause statements ('A key area for further inquiry is understanding how...').
**Human target:** Poses questions as direct rhetorical questions embedded in the prose flow ('How then should marketers...?', 'What are the primary motivations that...?').
**Rule:** Convert 'This raises a question: X?' meta-frames and noun-clause statements ('it is worth investigating whether X') into direct rhetorical questions embedded in the flow ('Does X?').
**Examples:**
- BEFORE: This raises a key question for marketers: how can innovation opportunities be identified in ways that align with BW principles?
  AFTER : How then should marketers identify promising innovation opportunities that align with BW objectives?
- BEFORE: A key area for further inquiry is understanding how consumers make decisions related to investing in and collecting enrichment goods. Research should explore the primary motivations that prompt consumers to begin collecting
  AFTER : What are the primary motivations that drive consumers to start collecting and how does that impact their purchase decisions?

## Defined-term and vocabulary consistency  [tier: low]
**LLM signature:** Drifts from the paper's defined vocabulary and varies elevated synonyms: 'modern B2B buyers', 'well-rounded salespeople', 'capabilities', and rotating synonyms for one referent ('underserved area', 'underprivileged neighborhood', 'disadvantaged neighborhood').
**Human target:** Uses the paper's established terms consistently: 'today's B2B buyers', the defined 'holistic salespeople'/'sales reps', 'competences', and one consistent plain descriptor ('deprived area') throughout.
**Rule:** Replace temporal 'modern'->'today's'; use the paper's defined term ('holistic salespeople' not 'well-rounded salespeople'); pick one consistent descriptor for a recurring referent and drop register-varying synonyms (underserved/underprivileged/disadvantaged->'deprived').
**Examples:**
- BEFORE: the evolving behaviors and expectations of modern B2B buyers, who are demonstrating greater discernment
  AFTER : the changes in behaviors and expectations of today's B2B buyers, who are becoming more judicious
- BEFORE: residing in an underserved area of Rio de Janeiro
  AFTER : who lived in a deprived area of Rio de Janeiro
