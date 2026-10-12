CONFIDENTIAL — DO NOT DISTRIBUTE — RAG LECTURE TRANSCRIPT — page 1
================================================================
RAG LECTURE TRANSCRIPT (auto-captured, lightly cleaned)
Course: From LLM APIs to RAG Systems | 41 slides | speaker notes merged
NOTE FROM TRANSCRIBER: slide layout markers were kept inline as "== slide N ==";
figures were replaced with a short description in square brackets. Timestamps
were removed. Captions below figure descriptions are verbatim from the deck.

== slide 1 == Limitation #1: The Knowledge Cutoff. Weights are frozen after
training. Zero new information enters the brain. FAMOUS CHATGPT BEHAVIOR: "My
knowledge cutoff is September 2021. I do not have real-time information and
cannot access events, news, or stock prices after this date." Once pre-training
finishes, the weights are baked into silicon; the model lives permanently in the
year it was trained. Why can't we retrain it every day? Training costs millions
of dollars and weeks of supercomputing time. Feeding new data directly causes
Catastrophic Forgetting (it overwrites older facts). Pre-training is too heavy
for continuous updates.

== slide 2 == Limitation #2: The Context Window. The model has zero permanent
memory; it only sees an active sliding window. The sliding window in action:
Msg 1 "My name is Alice and I am an architect" — DROPPED (out of window);
Msg 2 "Assistant: Nice to meet you Alice!" — DROPPED. Active context window
sees Msg 15 "Let's redesign the structural floorplan", Msg 16 the assistant's
updated blueprint, Msg 17 "By the way, what was my name again?", and the
assistant answers "I'm sorry, you haven't mentioned your name yet!" The
stateless goldfish: every API call is completely independent; the server
re-sends the whole chat transcript every single turn. Once your chat exceeds
the token budget (for example 4k or 8k tokens in GPT-3.5), earlier messages get
chopped off forever. 2026 perspective: modern models feature 128k to 2M+ token
windows, but long contexts are expensive, slow down inference, and suffer from
the "lost in the middle" effect. Managing context is core engineering.

== slide 3 == The Rulebook Problem. 1 token is about 0.75 words. 1 PDF page is
about 500 words. A 900-page rulebook is 450,000 words, about 600,000 tokens.
A 256K context window holds roughly 384 pages of plain text. Window: 256,000
tokens x 0.75 = 192,000 words. Pages: 192,000 / 500 = about 384 pages. Rulebook:
900 x 500 x 1.33 = 600,000 tokens. The window must also hold the system prompt,
the conversation, and the answer, so the budget left for your data is even
smaller. Problem 2: even if it fit, every request pays. Frontier model example
price: $2.50 per 1M input tokens, so 600,000 tokens x $2.50 / 1,000,000 = $1.50
per request. Budget model example price: $0.15 per 1M input tokens, so 600,000 x
$0.15 / 1,000,000 = $0.09 per request. Stateless API: the book is re-sent every
turn, so a 10-turn chat costs about $15 at frontier pricing. 1,000 questions/day
at $1.50 = $1,500/day, about $45,000/month. At budget pricing that is $90 per
day for 1,000 questions, and none of this includes output tokens or the wait
time for a huge prompt.

CONFIDENTIAL — DO NOT DISTRIBUTE — RAG LECTURE TRANSCRIPT — page 2

== slide 4 == The RAG Genesis. 2020: Facebook AI Research noticed we already
rewrite every prompt before the model reads it. Their idea: rewrite it with the
missing knowledge. [Figure: first page of the RAG paper.] NeurIPS 2020,
"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", Patrick
Lewis et al., Facebook AI Research, UCL, NYU. Quote: "Large pre-trained language
models have been shown to store factual knowledge in their parameters... However,
their ability to access and precisely manipulate knowledge is still limited...
updating their world knowledge remain open research problems." The raw user text
never reaches the model; the application assembles persona, rules, history, and
the user turn into a prompt template with special tokens (for example
<|im_start|>system ... <|im_end|>). So put the knowledge in the prompt: fetch the
few relevant pages and inject them as context. No retraining, and no 600K-token
rulebook on every request.

== slide 5 == RAG: Retrieval-Augmented Generation. Retrieve: the app searches
the knowledge base and pulls the most relevant parts. Augment: add those parts
to the prompt next to the user question. Generate: the LLM reads the context and
answers. Worked example: question "How many vacation days do new employees get?"
Retrieved chunk: "Policy 4.2 New employees receive 21 paid vacation days per
year." The other candidate chunks in the search results were Policy 1.1 working
hours 9:00 to 17:00 Sunday to Thursday, Policy 7.3 expense reports due on the
first of each month, and Policy 9.1 visitor badges returned at the front desk.
Step 3 output: "New employees receive 21 paid vacation days per year (Policy
4.2)." Prompt is about 500 tokens, cost about $0.0013, roughly 1,200x cheaper
than pasting the whole rulebook.

== slide 6 == Retrieval: How Do We Find the Relevant Part? Indexing time (once
per document): PDF or knowledge base -> chunks -> embedding model -> stored
vectors. An embedding model is an encoder-only transformer; it returns a dense
vector, typically 768 to 1,536 numbers. Similar meanings land at nearby
coordinates. Query time (every question): the question is embedded with the same
model, then compared against every stored vector using cosine similarity; the
closest vectors are the retrieved chunks. Use two different embedding models and
the comparison breaks: the vectors no longer live in the same space. Example
cosines: Policy 4.2 Leave and Time Off cos 0.91; Policy 1.1 Working Hours cos
0.64; Policy 7.3 Expense Reports cos 0.52. No shared keywords needed: "vacation
days" matches the meaning of "paid vacation days per year".

== slide 7 == Wait: Doesn't the Encoder Have a Limit Too? It cannot embed an
entire 900-page rulebook, so it never tries. Chunking: 900-page rulebook ->
split into chunks -> embed one by one -> one vector per chunk. Numbers:
900 pages is about 600,000 tokens; chunk size about 150 tokens; about 4,000
chunks; 4,000 vectors stored. A question then costs one embedding plus 4,000
tiny comparisons. No 600K-token prompt anywhere.

CONFIDENTIAL — DO NOT DISTRIBUTE — RAG LECTURE TRANSCRIPT — page 3

== slide 8 == Fixed-Length Chunking. Cut the text every N tokens no matter what
it says. Hyperparameters: chunk_size 500 tokens, chunk_overlap 50 tokens (10%).
A band of overlap is repeated at the edges so a sentence split by a cut still
appears whole in one of the chunks. Example: chunk_017 ends "...leave must be
recorded" and chunk_018 starts "in the personnel file...". Small chunks give
precise matches, less context per hit. Large chunks give more context, fuzzier
matches, longer prompts. Problems: cuts land mid-sentence, mid-table, or
mid-code block; overlap duplicates text causing near-duplicate results and
wasted storage; the size is blind to structure, so a table row gets the same
budget as a page.

== slide 9 == Sentence-Based Chunking. Split after punctuation, then group a
fixed number of sentences. Hyperparameters: sentences_per_chunk 3, overlap
1 sentence, boundary rules ".", "?", "!", newline. The splitter cuts after
punctuation then groups; example: chunk 1 = S1 S2 S3, chunk 2 = S3 S4 S5 (S3
sits in both, overlap = 1 sentence). Sentence splitting is language work:
abbreviations like "Policy No." and "e.g." break naive splitters. Problems:
abbreviations and decimals cause false boundaries; a single sentence is often
too small to carry meaning alone; fixed sentence counts still cut a topic
mid-thought.

== slide 10 == Paragraph-Based Chunking. Let the author do the chunking: split
on paragraph breaks. Hyperparameters: max_tokens 500 (split oversized),
min_tokens 80 (merge tiny ones), separator blank line. Example: P1 40, P2 60
(merged because too small), P3 900 (split into two chunks at the nearest
sentence before the limit), P4 50. Problems: PDFs lose blank lines, so columns,
tables, and headers break the format; paragraph sizes vary wildly, one line here
and a full page there; one paragraph can quietly hold several different topics.

== slide 11 == Semantic Chunking. Split where the meaning changes, not where the
punctuation falls. Sentences are embedded and compared with their neighbour;
when similarity drops below a threshold, cut. Hyperparameters:
similarity_threshold 0.75 (cut below), min/max chunk 200/800 tokens, detector:
an extra embedding pass over the document. Example: a section drifts from
vacation days to lunch breaks to dress code; the splitter cuts twice and returns
three coherent chunks instead of five mechanical ones. Problems: costs an extra
embedding pass; the threshold is data-dependent and needs calibration; chunk
sizes become unpredictable.

== slide 12 == Recursive Chunking. Try the biggest separator first, then fall
back to smaller ones until the chunk fits. Hyperparameters: separators "\n\n",
"\n", ". ", " ", ""; chunk_size 500 tokens; chunk_overlap 50 tokens. Example:
Section 4 is 900 tokens, too big; split by paragraphs gives para A 420 and para
B 480 (still too big); split B by sentences, then merge neighbours back up to
the size limit. This is the default design behind most libraries that ship a
"recursive" text splitter. Problems: the separator list must match the format
and the language; at the leaf level it is still a mechanical size cut; it is the
most complex method to reason about and to debug.

CONFIDENTIAL — DO NOT DISTRIBUTE — RAG LECTURE TRANSCRIPT — page 4

== slide 13 == Child-Parent Chunking. Retrieve small, feed big: match on child
chunks, send the parent section to the LLM. Hyperparameters: child_size 150
tokens (indexed), parent_size 1,200 tokens (sent), mapping child_id to
parent_id. Example: the question matches child chunk "New employees receive 21
paid vacation days"; the prompt receives the entire Section 4, so the model also
sees the rollover rules and the part-time rules. Problems: storage doubles;
parents can be too big or include noisy neighbouring text; prompt cost grows
with parent size, so it needs tuning.

== slide 14 == Are We Over? Not Even Close. Other methods (partial list): token
sliding windows, markdown headers, code-aware (AST), table-aware, page-aware,
layout-aware (PDF), proposition based, agentic or LLM-chosen. Match the method
to the data: documents with headings split on headings; source code split on
functions; contracts split on clauses; chat logs split on turns. Nothing stops
you from inventing your own method. The right chunk is the one your data already
believes in. Chunking is the highest-leverage decision in RAG.

== slide 15 == Where Do 4,000 Vectors Live? A vector database stores vectors as
keys and text as values, then searches by distance instead of exact match. Each
chunk keeps three things together: the vector (768 numbers), the original text,
and metadata like source file and page. A Chroma row: key [0.12, -0.98, 0.44,
...] 768 numbers; value "Policy 4.2 New employees receive 21 paid vacation
days..."; meta { source: "rulebook.pdf", page: 412 }. Chroma is the popular
default for local work and is literally a SQLite database under the hood:
chroma.sqlite3, pip install chromadb, no server. col.add(ids=[...],
embeddings=[...], documents=[...]); col.query(query_embeddings=[q],
n_results=3). Alternatives table: Chroma = embedded, file based; prefer for
local dev, prototypes, small and medium sets (this lecture). FAISS = search
library from Meta; prefer for in-memory experiments where you build your own
storage. Qdrant = open-source server in Rust; prefer for self-hosted production
with payload filters and hybrid search. pgvector = Postgres extension; prefer
when you already run Postgres and want SQL, joins, transactions. Pinecone =
managed cloud service; prefer for zero ops and elastic scale when the budget
allows. Milvus = distributed cluster; prefer for billions of vectors and a
platform team to run it. Also Weaviate, LanceDB, Redis, Elasticsearch. The
retrieval math is identical everywhere; the choice is operational fit.

== slide 16 == How Do We Know RAG Works? It starts with a dataset: the Golden
Set (one row per test question) with columns Question, Expected answer, Relevant
chunks. Example rows: "How many vacation days do new employees get?" -> 21 days
per year (Policy 4.2), chunks chunk_112 and chunk_113; "Can visitors enter the
lab after 18:00?" -> No, badges are disabled at 18:00, chunk_204; "How are
expense reports submitted?" -> Monthly, through the finance portal, chunks
chunk_301 and chunk_302. 50 to 200 questions, written by people who know the
domain. One system run gives two outputs to score: the chunks and the answer.
Two levels to evaluate: retrieval — did we fetch the right chunks? — and
generation — is the answer faithful and correct? A perfect answer cannot come
from the wrong context, so retrieval is scored first.

CONFIDENTIAL — DO NOT DISTRIBUTE — RAG LECTURE TRANSCRIPT — page 5

== slide 17 == Precision and Recall. Knowledge base holds 3 relevant chunks:
112, 113, 204. Top 5 retrieved: 112 ok, 118, 203, 090, 113 ok — so 2 relevant,
3 noise, and 204 was never found. precision@5 = relevant retrieved / retrieved
= 2/5 = 0.40. recall@5 = relevant retrieved / all relevant = 2/3 = 0.67. Low
precision means noise: extra cost, distraction, worse answers. Low recall means
missing facts: the model cannot answer what never arrived. Trade-off: bigger k
raises recall and lowers precision; smaller k does the opposite. Also watch hit
rate (did we get at least one relevant chunk?) and MRR (how high did the first
relevant chunk rank?).

== slide 18 == Faithfulness. faithfulness = supported claims / total claims.
The judge reads the answer, breaks it into claims, and checks each one against
the retrieved context only; outside knowledge does not count, even when it is
true. Example: context says "New employees receive 21 paid vacation days per
year. Leave must be requested 3 days in advance." The claims "21 paid vacation
days" and "3 days notice" are supported; "unused days can be cashed out" is not
in context; faithfulness = 2/3 = 0.67. In practice a stronger LLM acts as the
judge (LLM-as-a-judge) with a human-reviewed sample; RAGAS automates the loop.
A faithful answer can still be wrong if retrieval failed; an unfaithful answer
is a hallucination. The model is allowed to answer "the policy does not mention
that".

== slide 19 == Answer Relevance and Correctness. relevance = does the answer
address the question asked? Measuring relevance trick: ask the judge to write
the question that the answer would answer, then compare it with the real
question using embeddings and cosine similarity. correctness = answer matches
the golden answer; exact match is too strict for prose, so the judge grades
semantic agreement. Reading numbers together: high relevance with low
correctness means it answers the question with wrong facts; high correctness
with low faithfulness means the right answer came from outside the context; all
low means retrieval is broken, fix it first. Scores should point at the stage to
repair.

== slide 20 == The RAG Scorecard. Five metrics: Precision@k (retrieved chunks
that were relevant, retrieval stage), Recall@k (relevant chunks that were
retrieved, retrieval), Faithfulness (answer claims supported by the context,
generation), Answer relevance (the answer addresses the question, generation),
Correctness (the answer matches the golden answer, generation). The loop: golden
set -> run system -> score -> fix the weakest stage -> repeat. Change one
variable per run so the scores mean something. Use a strong judge model with
fixed rubrics and a human-checked sample of 20 to 50 rows.

== slide 21 == That Was Naive RAG. The baseline: chunk -> embed -> store ->
retrieve -> augment -> generate. One fixed chunking strategy, one vector search,
top-k chunks straight into the prompt. Good enough for clean, uniform text. One
size does not fit all: legal contracts need clause chunks and keyword hybrid;
source code needs function and AST chunks; support tickets need conversation
turns; tables and PDFs need layout-aware parsing. Upgrades coming: hybrid search
(vector + keyword), query rewriting, reranking, metadata filters, multi-hop
retrieval, child-parent feeding, better chunking, evaluation loops. A RAG system
is software engineering: compose, measure, keep what improves the scores. Naive
RAG is the baseline, not the ceiling.

== slide 22 == When Meaning Is Not Enough. Embeddings compress meaning, and
compression drops the exact bits: codes, numbers, names, and logic words.
Identifiers and codes: query "fix ERROR E-1042" gets cos 0.97 against the
retrieved chunk "E-1043: restart the gateway" — the wrong fix. One character
apart, two different problems, nearly identical vectors. Numbers and versions:
"Policy 4.2: 21 days" cos 0.98 against "Policy 4.3: 15 days" — the wrong
answer; in embedding space 4.2 and 4.3 are neighbours, in policy land they are
different rules. Negation and logic: "dental is not included for contractors"
cos 0.91 against "dental is included for contractors" — opposite meaning; a
single "not" flips the fact but barely moves the vector. Rare and invented
words: internal acronyms, product names, and project codes like "NTI-SSO" have
no training history; the encoder falls into a generic cluster and retrieval
returns generic chunks. The fix is not more vectors; it is exact matching for
the exact things, alongside the semantic search.

CONFIDENTIAL — DO NOT DISTRIBUTE — RAG LECTURE TRANSCRIPT — page 6

== slide 23 == Lexical Search: Match the Actual Words. The inverted index maps
every token to the chunks that contain it: "vacation" -> chunk_112, chunk_115,
chunk_118; "4.2" -> chunk_112; "E-1042" -> chunk_090. Lookup is exact, instant,
easy to explain. The three signals: term frequency (how often in this chunk),
document frequency (how rare across the corpus), length (how long the chunk is).
Rare terms separate documents; common terms separate nothing. The family:
TF-IDF (the classic term weighting), BM25 (the refined industry standard), LSA
(matrix factorization for latent meaning).

== slide 24 == TF-IDF: Rare Words Win. A term matters if it appears often in
this chunk and rarely in the whole corpus. "vacation" is rare in corpus and
frequent here: high weight. "policy" is in every chunk: near zero weight.
Formulas: idf(t) = ln(N / df(t)); score(q, d) = sum of tf(t, d) x idf(t), where
N = number of chunks and df = how many chunks contain the term. Example with
4 chunks and query "vacation days": idf("vacation") = ln(4/2) = 0.69
(informative); idf("days") = ln(4/4) = 0.00 (everywhere); chunk_112 has
vacation x3 so score 2.08; chunk_118 has vacation x1 so score 0.69. Problems:
no synonyms, so "PTO" finds nothing even with vacation documents nearby; length
bias, because long chunks accumulate term matches; raw counts, because the 10th
mention counts as much as the second.

== slide 25 == BM25: TF-IDF, Fixed. Two fixes: diminishing returns
(saturation) when a term repeats, and length normalization so a long chunk
mentioning a term once is weaker evidence than a short chunk mentioning it once.
Formula: score = idf(t) x (tf x (k1 + 1)) / (tf + k1 x (1 - b + b x len /
avg_len)). Typical settings: k1 = 1.2 (saturation), b = 0.75 (length penalty).
Example: a 90-token policy chunk and a 900-token handbook page both mention
"vacation" 3 times; BM25 ranks the short chunk first because it has the same
evidence with less noise around it. Problems: still no synonyms; tokenizer
rules matter for "4.2", "E-1042", Arabic, and code; spelling variants like
"email" vs "e-mail" are separate terms.

== slide 26 == LSA: Latent Semantic Analysis. The 1990s bridge: terms x chunks
matrix -> SVD -> top k concepts -> vectors in k dimensions. X (terms x chunks)
≈ U Σ Vᵀ, keep the top k singular values; queries and chunks are projected into
the same k-dimensional concept space, then compared with cosine similarity.
Example: "automobile accident" can match "car crash" with zero shared words
because both load on the same latent dimensions. But "Policy 4.2" against
"Policy 4.3" stays blurred; latent concepts do not preserve exact numbers.
Problems: static, the factorization is rebuilt when the corpus changes; k is a
tuning knob with no formula; weaker than modern embeddings and harder to
explain.

== slide 27 == Learn the Weights, Do Not Guess Them. score = w1 x cosine +
w2 x BM25 + w3 x exact_match + b. Hand-tuned weights are guesses; with labeled
query and chunk pairs from the golden set, linear or logistic regression learns
the weights. This is the simplest form of learning to rank. Features: cosine
(semantic score), BM25 (lexical score), exact term overlap (0 or 1), optional
same-section or recency. Example with 100 labeled questions: semantic only gives
recall@5 0.72; BM25 only gives recall@5 0.80; learned fusion gives recall@5
0.91. Problems: needs labels; small sets overfit, so regularize and keep a
held-out split; linear only, cannot capture complex feature interactions.

CONFIDENTIAL — DO NOT DISTRIBUTE — RAG LECTURE TRANSCRIPT — page 7

== slide 28 == Which K Should You Choose? With 3 relevant chunks in the ranked
list: k=3 gives precision 2/3 = 0.67 and recall 2/3 = 0.67; k=10 gives
precision 3/10 = 0.30 and recall 3/3 = 1.00. Small k: tight clean prompt, but
the chunk at rank 9 never arrives and the answer needs it — high precision,
capped recall. Large k: every relevant chunk makes it in, but so does the noise,
tokens cost more, and useful evidence gets buried in the middle — high recall,
collapsing precision. Can we have both? Yes, by splitting the job: a cheap
retriever casts a wide net at high k, then a smarter reranker puts the true best
5 on top. Retrieval for recall, reranking for precision.

== slide 29 == Learning to Rank. Reranking is a supervised learning problem with
one twist: the answer is an order, not a number. Three families: pointwise
(score each candidate alone), pairwise (learn "A should rank above B"), listwise
(optimize the whole list against a ranking metric). Famous models: RankNet
(pairwise, neural), RankSVM (pairwise, margins), LambdaMART (listwise, boosted
trees), LightGBM ranker (LambdaMART today). LambdaMART weights every ranking
error by how much the metric would improve. Relevant or not is not enough; the
model reads the top 5, so a useful chunk at rank 9 is worth almost nothing.

== slide 30 == NDCG: Reward the Right Order. DCG = sum of gain / log2(rank + 1);
NDCG = DCG / IDCG. Every relevant chunk adds a gain; the further down it sits,
the harder the position discounts it; IDCG is the score of the perfect ordering,
so NDCG lands between 0 and 1. Worked example with relevant chunks at ranks 2, 5,
and 9: DCG = 0.63 + 0.39 + 0.30 = 1.32; IDCG for ranks 1, 2, 3 = 1.00 + 0.63 +
0.50 = 2.13; NDCG@10 = 1.32 / 2.13 = 0.62. Position discounts: rank 1 = 1.00,
rank 2 = 0.63, rank 5 = 0.39, rank 10 = 0.30. A useful chunk at rank 1 counts
about 3.3x one at rank 10. Precision and recall do not care about position;
NDCG is what rerankers are trained and judged on because the prompt only reads
the top few chunks. LambdaMART adjusts weights by how much NDCG a swap would
gain; that boost is the "lambda".

== slide 31 == Retrieve Wide, Rerank Narrow. Architecture: query -> retriever
top 100, fast -> reranker scores pairs -> top 5 into the prompt. Stage 1: the
retriever uses bi-encoder embeddings, BM25, or a hybrid; optimized for recall,
get the right chunk into the candidate list even at rank 90; roughly 10
milliseconds for the whole knowledge base. Stage 2: the reranker is a
cross-encoder that reads the query and the chunk together, or a trained LTR
model scoring rich features; optimized for precision, it keeps the true best 5;
slow per pair, but only a hundred pairs per question. Before and after with 100
labeled questions: retriever recall@100 = 0.95; retriever precision@5 = 0.35;
reranked precision@5 = 0.80; reranked NDCG@5 = 0.88. Wide net, sharp filter: the
cheapest quality jump in all of RAG.

== slide 32 == When the Question Misses the Answer. Users ask in their own
words; documents are written in policy words. Example: user asks "my new hire
starts monday, how much time off do they get?"; the chunk says "Policy 4.2:
Employees receive 21 days of annual leave after probation."; cosine of the raw
query is 0.41 at rank 6, so a weaker chunk wins. Same question rewritten as
"annual leave entitlement for new employees": cosine 0.83, rank 1. Even better,
the hypothetical answer itself: "New employees receive 21 days of annual leave
per year." gives cosine 0.88, rank 1. Answers look like documents, so they match
documents better than questions do. The fix is not a better vector; the fix is a
better query: transform it before searching. Three ways: rewrite it, answer it
first, or ask it many ways.

CONFIDENTIAL — DO NOT DISTRIBUTE — RAG LECTURE TRANSCRIPT — page 8

== slide 33 == Rewrite the Query Before You Search. Let the LLM translate the
user's words into document words: fix typos, casing, broken fragments; expand
acronyms and synonyms (PTO to annual leave); translate conversational style to
document style; strip greetings, filler, emotion. Example input: "my new guy
starts monday, how much time off does he get lol". Output JSON with queries:
"annual leave entitlement for new employees", "new employee vacation days
policy", "probation period leave policy". Use temperature 0 for stability, and
log every rewrite so a bad retrieval can be traced later. Problems: one extra
LLM call per question; the rewrite can drift from the real intent; prove it on
the golden set, a rewrite must raise recall.

== slide 34 == HyDE: Search With a Fake Answer. Hypothetical Document
Embeddings: questions are short and interrogative, documents are long and
declarative, so a drafted answer looks like a document and its vector lands
closer to the real document than the question vector does. Pipeline: question ->
LLM drafts an answer -> embed the draft -> vector search -> real chunks to the
prompt. The draft is only a search key; the final answer is generated from the
real retrieved chunks, never from the draft. Example: question "how much time
off does a new hire get?"; draft (details may be wrong) "New employees
typically receive 20 to 25 days of annual leave after a probation period."
Draft embedding vs Policy 4.2: cos 0.88, rank 1. Caveats: the draft can
hallucinate in a misleading direction; weakest on private domains; extra LLM
call per question.

== slide 35 == Multi-Query: Ask It Several Ways. One phrasing is one bet.
Generate 3 to 5 variants, retrieve for each, and merge. Pipeline: question ->
LLM N variants -> N retrievals -> merge + dedupe (RRF) -> rerank to top 5.
Reciprocal rank fusion is the standard merge: rank based, no score calibration
needed. Example: "annual leave policy" retrieves chunk_112, chunk_115; "vacation
days entitlement" retrieves chunk_112, chunk_118; "PTO rules for new hires"
retrieves chunk_204. Three phrasings, one union; chunk_204 was invisible to the
original wording. Caveats: N times the search cost, so parallelize; the merge
strategy matters as much as the generation; more candidates means more for the
reranker to remove.

== slide 36 == Decomposition: Break the Question Apart. Some questions are two
questions wearing one coat. A single embedding cannot cover two topics; a
question about carryover and payout pulls in two directions and retrieves the
average of both, which matches neither. Pipeline: complex question -> LLM
sub-questions -> retrieve each -> answer each part -> synthesize one answer.
This is least-to-most prompting wearing retrieval clothes. Example question:
"can I carry unused vacation days into next year and get paid for them when I
leave?" Sub-question 1: vacation carryover rules. Sub-question 2: payout of
unused leave on termination. Retrieved chunk_112 and chunk_117. Caveats: not
everything should be split, simple lookups get worse; sub-questions can drift
from the original intent; more calls, more retrievals, more latency.

== slide 37 == Documents Are Not Just Text. A real document is paragraphs,
tables, charts, org charts, floor plans, UI screenshots, scanned signatures,
product photos. A text-only index reads the words around the figure and none of
the figure. Text-only RAG goes half blind: "what does the new badge look like?"
— answer is a photo on page 88; "who reports to the CTO?" — an org chart, the
text just says "see Figure 3"; "which warning sign is on the boiler?" — a scan,
no text at all. Multimodal RAG adds text chunks and image vectors in the same
searchable index; the query can be text, an image, or both; the generator is a
vision-capable LLM. Ingredients: vision encoder (ViT), text encoder, shared
space (CLIP-style or a captioning VLM shortcut), and a multimodal generator.

CONFIDENTIAL — DO NOT DISTRIBUTE — RAG LECTURE TRANSCRIPT — page 9

== slide 38 == One Space for Text and Images. CLIP (2021) trained an image
encoder and a text encoder together, so a word and a picture can land near each
other. [Figure: CLIP contrastive pre-training, figure 1 of the CLIP paper.]
Matching image/caption pairs are pulled close; mismatched pairs are pushed
apart. Two encoders, one space: ViT for images, a text transformer for captions,
trained contrastively on 400M image-caption pairs. Rhino vs dino example:
"a photo of a rhino" x rhino image = 0.88; "a photo of a dino" x rhino image =
0.24; "a photo of a dino" x dino image = 0.86; "a photo of a rhino" x dino
image = 0.22. Change one word and the match flips; the two encoders agree
without sharing a single token.

== slide 39 == Multimodal RAG in Practice. Pipeline: text + images -> one mixed
index; query text or image -> VLM answers with text and pictures. Two ways to
index images: caption-first (a VLM writes captions and you index them as text;
simple, loses detail) or embed-images (CLIP-style vectors in the shared space;
detail kept); the usual answer is both, plus an image id to file path mapping
for the prompt. Example queries: "what does the visitor badge look like?"
returns the badge photo plus the policy paragraph; sending a photo of a damaged
part asks "is this covered by the warranty?". Caveats: images are expensive
tokens; scans need OCR and captions lose skipped details; add image-bearing rows
to the golden set or image retrieval goes untested.

== slide 40 == Graph RAG: Retrieve Relationships. Chunks are islands; some
questions need the connections between them. Where chunk RAG stops: multi-hop
"who manages the team that owns the payroll system?" and global "what are the
main themes across the whole rulebook?" Vector search returns chunks one by one;
nothing connects a fact in chunk 12 to a fact in chunk 340. A graph adds nodes
(Employee, Team, System, Policy), edges (manages, owns, reports_to, covers), and
communities (clusters with LLM summaries). An extraction pass has the LLM read
the chunks and write down who relates to what. Multi-hop walk example: question
"who manages the payroll team?" -> find node Payroll Team -> follow edge manages
-> answer Alice. Costs: building the graph costs an LLM pass over the whole
corpus; extraction is error-prone and a wrong edge poisons retrieval; worth it
for multi-hop and global questions, overkill for lookups.

== slide 41 == Knowledge Graph RAG: Ask the Graph. Triples: (Alice, manages,
Payroll Team), (Payroll Team, owns, Payroll System), plus a schema of allowed
types and relationships. Pipeline: question -> link entities -> translate to a
graph query -> run it, collect facts -> answer with citations. The LLM writes
Cypher or SPARQL and the database executes it deterministically. Example:
question "who manages the team that owns payroll?" becomes MATCH
(e:Employee)-[:MANAGES]->(t:Team)-[:OWNS]->(s:System {name: "Payroll"}) RETURN
e.name — two hops, one query, zero guessing. Pros: precise, auditable, easy to
update, compliance friendly. Cons: needs schema work and clean entity
extraction; sparse coverage, what never became a triple cannot be found;
text-to-query translation breaks on complex questions.

CONFIDENTIAL — DO NOT DISTRIBUTE — RAG LECTURE TRANSCRIPT — page 10
