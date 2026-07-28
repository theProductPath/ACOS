---
type: acos-doc
subject: building-a-rag
status: active
last-updated: 2026-07-28
maintainer: Steven Jones
purpose: Optional bonus guide — how to stand up a local retrieval-augmented-generation (RAG) layer over an ACOS instance, why ACOS's own conventions make that build meaningfully easier than it would be over an unstructured company tree, and a copy-paste brief you can hand to a coding agent to build it.
---

# Building a RAG over your instance

This is a bonus guide, not a step in adoption. Nothing here is required to run an ACOS instance, and nothing in the framework depends on it — skip it entirely if progressive-disclosure scanning (an agent reading folder READMEs in cascade) already answers your questions fast enough. Reach for this when your instance has grown large enough, or your agents ask it questions often enough, that you want a kept-warm index they can query directly instead of walking folders from scratch every time.

It's written for someone who already has a working ACOS instance and wants to add retrieval on top of it — not for someone setting one up for the first time (that's [`adopting-acos.md`](adopting-acos.md)) or extending the framework itself (that's [`extending-acos.md`](extending-acos.md)).

## Why this is easier over an ACOS instance

A retrieval system's quality ceiling is set by four properties of the corpus underneath it, and disciplined ACOS operation supplies all four as a byproduct — not as RAG-specific work you'd do on purpose.

**Structure and chunkability.** Markdown-first, one-concept-per-file, heading-structured content splits into coherent, self-contained passages for free. A company living in scattered docs, chat threads, and email has to manufacture that structure before it can even chunk well.

**Metadata for precision.** Consistent frontmatter — `type`, `status`, `purpose`, `maintainer`, `last-updated`, `tags`, `related-decisions`, `superseded-by` — gives a retriever a real facet schema. "Active clients only," "decisions related to X," "what changed recently" become one-line filters instead of guesswork. This is the biggest quality lever past the embedding model, and it only exists because you were maintaining it for operating discipline, not for search.

**Lifecycle and freshness.** `status`, `last-updated`, `superseded-by`, and a decisions log with explicit supersession encode currency in the data itself, so an index can downrank dead content using the corpus's own signals instead of a separate staleness heuristic.

**Canonical topology.** ACOS already declares what's authoritative and what to skip: the root's `## Folder map` allowlist, briefs as substance versus READMEs as front doors, and the [agent-ignore](../framework/agent-ignore.md) underscore convention for `_archive/` and `_progress/`. That's exactly the "what to index, what to ignore" decision every RAG build has to make from scratch — yours is already made.

None of this makes the build free. It makes the build *tractable* — the parts that are usually the hard, bespoke, expensive-to-get-right parts of a RAG project are instead a direct readout of conventions you're already following. What's still yours to do is real: picking a stack, building the pipeline, and — the part every real RAG needs regardless of corpus — a short calibration pass, covered below.

## What "done" looks like

Two front doors on one shared index, and you can build either or both:

- **An MCP tool** (`search_tppos`-shaped: a `search` tool plus a `get_document` tool) exposed to any MCP-capable host — Claude Desktop, Cursor, Cline, or your own agent tooling. This is the higher-value one to build first: it costs nothing new because you already work through an agent, and it hands ranked, cited passages to a strong model for synthesis rather than trying to generate answers locally.
- **A standalone chat interface** — a local model (or a hosted one) answering directly over the same retriever, useful as an "ask my instance" box that doesn't require an agent host. Optional, and it can come later without touching the retrieval core.

Build the retrieval core once; both front doors are thin layers over the same index. Don't build the chat UI before the retriever is good — a fluent wrong answer is worse than a slow right one.

## Reference stack

A validated default, with the swap points that matter. None of these choices are load-bearing for the ACOS-specific parts of the design below — the metadata lift, the exclusion rules, the lifecycle-aware ranking all transfer to any stack with hybrid search and a metadata filter.

| Layer | Reference choice | Why | Swap for |
| --- | --- | --- | --- |
| Orchestration | LlamaIndex | Document loaders for markdown+frontmatter, pdf, docx, pptx, xlsx; an ingestion pipeline with content-hash dedup for cheap incremental updates. | Any framework with the same shape — LangChain, Haystack, or a hand-rolled pipeline if your corpus is small. |
| Vector store | LanceDB (embedded, on-disk) | No server, no Docker; native hybrid keyword + vector search and metadata filtering over nested fields — this matters a lot for a corpus full of proper nouns (client names, product codenames, decision numbers). | Chroma, Qdrant, or a managed vector DB if you want it hosted. Keep hybrid search as a hard requirement (see below on why). |
| Embeddings | Ollama `bge-m3`, local | Local, hybrid-friendly, no per-query cost, runs on Apple Silicon or any machine with a decent GPU. | Any hosted embedding API if local inference isn't available or the corpus is large enough that local embedding time matters. |
| Generation (for the chat front door only) | Ollama `qwen2.5:32b` or similar, local | Retrieval-only via the MCP front door lets a frontier model do synthesis when it matters; local generation is for the offline chat UI. | A hosted model, or skip this layer entirely if you're only building the MCP front door — the MCP server doesn't generate anything, it returns passages. |
| Freshness | Scheduled incremental reindex | Content-hash dedup re-embeds only changed/new/deleted files. | `launchd` on macOS, `cron` or a systemd timer on Linux, Task Scheduler on Windows — or just run it by hand after big edits if your instance doesn't change often. |

Rejected by default, and worth knowing why before you reach for them: a heavy document-understanding platform (the RAGFlow-shaped tools) — their value is deep parsing of messy scanned PDFs and tables, which is overkill if your corpus is mostly clean markdown; a paid embedding or vector-DB API as your only option — fine if you want it, but not a default for a corpus this size; running the pipeline inside a sandboxed cloud agent environment — indexing needs GPU access and a filesystem walk over your real instance, which usually means running it on a machine that actually has both.

## The build, as a brief for your agent

The fastest path is to hand this whole section to a coding agent (Claude Code, Cursor, or similar) working in a fresh repo *outside* your instance tree — treat the instance as read-only source, the same way ACOS treats a Drive-synced tree as the operating layer and the code that reads it as separate. Fill in the placeholders first.

````text
Build a local, hybrid retrieval-augmented-generation (RAG) pipeline over an
ACOS company instance. The instance root is <instance-root-path>; treat it as
READ-ONLY source. Build the code and index in a separate repo/folder, not
inside the instance tree.

STACK (adjust to taste, keep the shape):
- Orchestration: LlamaIndex (or equivalent) with an ingestion pipeline that
  supports content-hash dedup for cheap incremental re-indexing.
- Vector store: an embedded, on-disk store with NATIVE HYBRID SEARCH
  (vector + keyword/BM25) and metadata filtering over structured fields.
  This is a hard requirement, not a nice-to-have — see rationale below.
- Embeddings + generation: local (e.g. Ollama) or hosted, your call.

CORPUS WALK AND EXCLUSIONS:
- Walk the instance tree starting at <instance-root-path>.
- Honor the ACOS agent-ignore convention: skip any folder whose name starts
  with an underscore (_archive/, _progress/, or any future underscore-
  prefixed folder), at any depth. This is a stated ACOS convention, but it is
  NOT self-enforcing for indexing tools — the pipeline must implement it
  explicitly.
- Also skip standard non-content paths: .git, .obsidian or equivalent editor
  metadata, node_modules, __pycache__, .DS_Store, and any generated build
  output.
- Index the document tail too if present (pdf, docx, pptx, xlsx) — expect
  these to carry no frontmatter and need real parsing; don't assume markdown
  conventions apply to them.

METADATA LIFT (per chunk):
- From frontmatter, where present: type, status, purpose, owner/maintainer,
  last-updated, tags, priority, due, parent, project, client,
  related-decisions, superseded-by, title.
- Derived from path/content: sibling (the top-level folder name — Clients,
  Products, Projects, or whatever this instance actually uses), client or
  project name from the path, a decision/ADR number if the file matches the
  instance's decisions-log naming pattern, a doc_kind (readme / brief /
  decision / assessment / progress / skill / other) inferred from path and
  frontmatter type, a heading breadcrumb, and a stable deep-link back to the
  source (a file:// path, an obsidian:// URI, or whatever the instance's
  tooling can open).

SPECIAL HANDLING — read the instance's own README pattern conventions
(framework/README.md in the ACOS repo) before assuming a naive walk is
correct:
- ACOS READMEs are deliberately NAVIGATIONAL, not substantive — they route
  to a sibling brief.md rather than holding the real content themselves.
  A naive indexer over-weights front-door READMEs and under-retrieves the
  brief.md files where the substance lives. Tag top-level READMEs as
  navigational; index brief.md files as primary content.
- Files with a `superseded-by` key (or a `status` VALUE indicating
  supersession — check both, not just the key) should be downranked, not
  excluded — they may still be the right answer to a historical question.

RETRIEVAL DESIGN — hybrid, not vector-only:
- Every query runs through a vector (semantic) retriever AND a keyword/BM25
  retriever over the same chunks, fused with Reciprocal Rank Fusion.
  Rationale: an ACOS instance is dense with proper nouns, decision numbers,
  and acronyms — exact tokens a vector index will "smear" toward
  similar-looking content. Vector-only retrieval will frustrate exactly the
  identifier lookups done most often.
- A metadata pre-filter (status, sibling, client, doc_kind, superseded) is a
  separate, earlier stage that narrows candidates before hybrid search runs.
- PER-CHUNK CONTEXT HEADER: prepend a short header (title | file path | type
  | status | tags) to each chunk's text before embedding and indexing. Do
  this even though it looks redundant with the metadata fields — identifiers
  that live only in a filename or frontmatter title (a decision number, a
  spec's title slug) are otherwise invisible to both retrieval legs, because
  the chunking strips them from the body text.
- DE-DUPLICATE BY SOURCE FILE in the top-k results — without this, one large
  or repetitive file can crowd out every other relevant source.
- LIFECYCLE-AWARE RANKING, applied at query time (no re-index needed to
  tune): demote raw/unsynthesized evidence (interview transcripts, raw
  scans) and archived or superseded paths; narrowly boost canonical kinds
  like decision and brief — NOT readme or assessment broadly, since those
  are common, navigational kinds that will flood unrelated queries if
  boosted indiscriminately. Demotions must SUPPRESS the kind-boost, not just
  multiply against it — a demoted document that also happens to be a
  canonical kind should stay demoted, not net out to "fine."
- ENTITY BOOST: when a query names a client or product, soft-boost results
  from that entity's own folder. Discover entities by scanning the
  container folders (Clients/*, Products/*, or whatever this instance's
  containers are named) for immediate subdirectories — this keeps the boost
  self-maintaining as new clients/products are added, with no code change.
- VOCABULARY ALIASES: maintain a small, explicit alias table for terms the
  corpus writes one way and a person is likely to ask another way (an
  acronym versus its expansion, an internal codename versus its plain-
  English description). This is corpus-specific and will need real
  examples from THIS instance — don't skip it; it closes a whole class of
  retrieval miss that no amount of structure fixes automatically.

FRONT DOOR — MCP server (build this one first):
- Two tools: a search tool (query, k, optional filters for sibling/status/
  doc_kind/client) returning ranked passages with rank, path, doc_kind,
  sibling, which retrieval leg matched, score, a deep-link, and a snippet;
  and a get_document tool (path, max_chars) that returns full file text,
  refusing any path that resolves outside the corpus root.
- Retrieval-only by design. Do not generate answers inside this server —
  hand passages to whatever model is calling it and let that model
  synthesize.
- Run over stdio for desktop hosts and optionally over HTTP for remote or
  non-Claude hosts. If you expose HTTP off-box, note it ships with no auth
  by default and needs a reverse proxy or tunnel with access control.

FRESHNESS:
- Support both a full reindex and a cheap incremental reindex keyed on
  content hash.
- Incremental upsert does not imply incremental delete — explicitly diff
  the index's tracked file list against what's actually on disk each run,
  and remove anything no longer present, from both the vector store and any
  separate metadata store.
- If any long-lived process (a chat server, an always-on service) holds the
  index open, know that it will pin a snapshot at open time and NOT see a
  later reindex until it's restarted or reopens the table — build a cheap
  way to detect this (report the pinned version vs. the latest version on
  disk) rather than assuming a fresh index means fresh answers everywhere.

EVAL:
- Before treating this as done, write 15-20 REAL questions you would
  actually ask, each mapped to a real source file you've verified still
  exists. Write them in your own words, not the corpus's — a question set
  authored while reading the corpus will inherit the corpus's vocabulary and
  silently hide vocabulary-gap failures.
- Include a validation step that checks every expected answer path still
  exists in the corpus before scoring anything — an eval set rots exactly
  like code when files get moved or renamed, and a stale expectation reads
  as a retrieval failure when it's actually a stale test.
- Report hit-rate@k and mean reciprocal rank (MRR). Tag questions by class
  (exact-identifier / conceptual / hybrid / vocabulary-gap) so a regression
  in one class doesn't hide in an aggregate number.

Build in phases: (1) ingestion pipeline with the exclusions, metadata lift,
and special-casing above; (2) hybrid retriever with the ranking rules; (3)
the MCP server; (4) the eval harness, run against real questions. Validate
each phase before moving to the next — a pipeline that "looks right" and a
pipeline that retrieves correctly are different claims, and only the eval
can tell them apart.
````

## Known pitfalls

These are failure modes that show up on real corpora, not synthetic ones, and they're worth designing around from the start rather than discovering after the fact.

**Duplicate-file crowding.** Without de-duplicating by source file, a single large or repetitive document can take multiple slots in your top-k and push the actually-relevant file out of the results window. Fix at query time: cap results per source file before truncating to k.

**Identifiers that live only in the filename or title.** A decision numbered `0013` or a spec with a distinctive title slug is invisible to both retrieval legs if the number or slug never appears in the chunked body text. A per-chunk context header (title, path, type, status, tags) prepended before embedding fixes this — it's the one tuning fix that requires a re-index rather than a query-time change.

**A demotion that quietly never fires.** Supersession, exclusion, and staleness rules are usually pattern-matched against frontmatter — and real corpora express the same fact multiple ways (a `superseded-by` key versus a `status` value that says the same thing). A rule that only checks one form will look tuned, pass a shallow test, and silently fail on the other form. Check both, and add a regression question for each form to your eval set.

**Ranking signals fighting each other.** A "canonical document kind" boost and a "this specific document is stale" demotion are different kinds of signal — one says *documents like this usually have answers*, the other says *don't want this document at all* — and if they're both plain multipliers in a chain, the boost can partially cancel the demotion and let stale content outrank the real answer. Demotions should suppress kind-boosts, not just multiply against them.

**Vocabulary gaps no amount of structure fixes.** ACOS's conventions give a retriever lifecycle, ownership, and document-kind signals — but they can't know that a person asks "proof of concept" while the corpus writes "POC," or that a person names a product by its casual nickname while every file uses the formal name. This is the one class of tuning that stays genuinely instance-specific: a short, hand-maintained alias table, built from real questions people actually ask.

**An eval that measures a different pipeline than the one that ships.** If query rewriting, aliasing, or boosting lives in the serving layer (a chat endpoint, an MCP handler) but the eval harness calls the bare retriever underneath it, the eval can report a great number while real answers are visibly wrong — because it's measuring a pipeline nobody queries. Route every consumer (CLI, MCP, chat, eval) through the same shared query-shaping step, so the thing measured is the thing shipped.

**A stale eval set masquerading as a retrieval bug.** When a folder gets reorganized, an eval question's expected path can go stale — and a stale expectation looks exactly like a real miss, except the retriever was right the whole time under the new path. Validate every expected path against the live corpus before scoring, and flag missing ones distinctly from real misses.

**A long-lived reader serving yesterday's index.** A process that opens your vector store once and holds it for its whole lifetime (a chat server, a background service) will keep answering from the snapshot it opened, even after a successful reindex writes a newer one — silently, with no error. If you run anything long-lived on top of the index, give it either a way to detect staleness (compare its pinned version to what's currently on disk) or an automatic restart tied to a successful reindex.

## Calibrating to your instance

Expect real tuning, and budget for it honestly rather than either over- or under-promising. The structural half of retrieval quality — lifecycle awareness, ownership, document-kind weighting, exclusions — is a reusable layer that transfers to any ACOS instance with almost no changes, because it's keyed on conventions every instance already follows. What stays genuinely yours is small: a short vocabulary-alias list built from how you actually ask questions, and maybe one content-type weight that reflects what your instance has a lot of.

So the honest framing is not "it just works" — no real RAG does, and a tool that hides its tuning knobs is worse than one that exposes them, because then you can't fix what's actually wrong. It's also not "expect a long tuning project." It's: build it, then spend roughly half an hour writing fifteen or twenty real questions in your own words, run the eval, and turn the two or three knobs it points you at. That's a bounded fitting step, not an open-ended one, and the eval harness is what keeps it bounded — without it you're tuning against vibes.

## What this doesn't solve

Worth stating plainly, because it's what keeps the pitch credible:

- The non-markdown document tail (PDFs, decks, spreadsheets) carries no frontmatter and needs genuine parsing — structure helps the markdown core of your instance, not the binaries sitting alongside it.
- A local generation model has a real quality ceiling versus a frontier model. Retrieval-only over MCP sidesteps this by handing passages to whatever model you're already working with; a standalone chat UI over a local model will feel that ceiling directly.
- "Kept up to date" is only ever as true as the job that actually reindexes — a scheduled task that silently stops running is indistinguishable, from the outside, from an instance that never changes.
- None of this replaces the [agent-ignore](../framework/agent-ignore.md) convention's own caveat: it's reliable for agents that read and honor it, not for indexing tools that walk the tree without consulting it. Your pipeline has to implement the exclusion itself — the convention doesn't enforce itself on tools that don't ask.

## Checklist

- [ ] Stack chosen (reference stack above, or your own swap), with hybrid vector + keyword search and metadata filtering as a hard requirement.
- [ ] Ingestion pipeline built: instance walk, underscore-prefix and standard exclusions, frontmatter lift, derived metadata, README-vs-brief special-casing, per-chunk context headers.
- [ ] Hybrid retriever built: RRF fusion, metadata pre-filter, de-dup by source file, lifecycle-aware weighting with demotions suppressing kind-boosts, entity boost, vocabulary alias table.
- [ ] MCP server built and registered in at least one host, exposing a search tool and a get_document tool, retrieval-only.
- [ ] Eval set written — 15-20 real questions in your own words, mapped to verified source paths, tagged by class — and a stale-path check wired into the harness.
- [ ] First eval run reviewed before trusting the index for real work; at least one tuning pass applied based on the misses.
- [ ] Freshness mechanism in place (scheduled or manual), and — if anything long-lived reads the index — a way to tell whether that reader is serving a stale snapshot.
- [ ] (Optional) Chat front door built once the retriever itself is solid.

## Related

- Framework manual: [`../framework/README.md`](../framework/README.md)
- Agent-ignore convention: [`../framework/agent-ignore.md`](../framework/agent-ignore.md)
- Adoption guide: [`adopting-acos.md`](adopting-acos.md)
- Extension conventions: [`extending-acos.md`](extending-acos.md)
- Reorganizing an instance: [`reorganizing-an-instance.md`](reorganizing-an-instance.md)
