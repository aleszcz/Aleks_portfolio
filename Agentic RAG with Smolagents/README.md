# Agentic RAG with Smolagents — Auto Insurance Claims Processing

This notebook builds an **Agentic RAG** application using the [`smolagents`](https://github.com/huggingface/smolagents) framework to automate the end-to-end processing of auto insurance claims. A single agent orchestrates a suite of specialized tools that parse a claim, validate it against policy records, retrieve relevant policy text from a vector database, sanity-check the claimed amount against real-world repair costs via web search, and produce a final structured decision.

## Business Context

Auto insurance claim handling is largely manual: executives parse invoices, cross-reference policies, and decide payouts by hand. This is slow, error-prone, and inconsistent. The notebook demonstrates an **Agentic RAG** alternative — where instead of a fixed RAG pipeline, an LLM agent decides which tool to call at each step, allowing it to branch (e.g., short-circuit on an invalid claim) and incorporate external signals (e.g., live web search for market repair costs).

## Architecture Overview

```
                        ┌──────────────────────────────────┐
                        │   ToolCallingAgent (GPT-4o-mini) │
                        │   + system + planning prompts    │
                        └──────────────┬───────────────────┘
                                       │ chooses tool
       ┌──────────┬──────────┬─────────┼──────────┬──────────────┬───────────────┐
       ▼          ▼          ▼         ▼          ▼              ▼               ▼
  parse_claim  is_valid  generate   retrieve   WebSearch    generate         finalize
   (JSON →    _query    _policy_   _policy_     Tool      _recommendation   _decision
   ClaimInfo)  (CSV     queries     text       (market    (LLM over claim   (→ ClaimDecision)
              lookup)              (ChromaDB)   prices)   + policy text)
```

Backing services:
- **LLM:** `gpt-4o-mini` via `OpenAIServerModel`
- **Embeddings:** `all-MiniLM-L6-v2` (Sentence-Transformers)
- **Vector DB:** ChromaDB collection `auto_insurance_policy`
- **Knowledge source:** `policy.pdf` chunked at 1000 chars / 200 overlap with `RecursiveCharacterTextSplitter`

## Notebook Workflow

### 1. Setup & Environment
- Installs `smolagents[toolkit]`, `chromadb`, `langchain-text-splitters`, `langchain-community`, `pypdf`, `openai`, and `ddgs` (DuckDuckGo search).
- Loads API credentials from `config.json` into environment variables.

### 2. Model & Embedding Initialization
- Instantiates the GPT-4o-mini model client.
- Sets up the `SentenceTransformerEmbeddingFunction` for ChromaDB.

### 3. Knowledge Base Construction
- Initializes a ChromaDB client and creates/gets the `auto_insurance_policy` collection.
- Loads `policy.pdf` with `PyPDFLoader`, splits it into chunks, and ingests the chunks (with metadata and IDs) into ChromaDB.

### 4. Schema Definitions (Pydantic)
Four `BaseModel` schemas enforce structured I/O between tools:
- `ClaimInfo` — claim number, policy number, claimant, date of loss, description, estimated repair cost, vehicle details.
- `PolicyQueries` — list of search queries to run against the policy KB.
- `PolicyRecommendation` — applicable policy section + recommendation text.
- `ClaimDecision` — claim number, covered (bool), deductible, recommended payout, notes.

### 5. Tool Definitions
Each tool is a `@tool`-decorated function the agent can invoke:

| # | Tool | Purpose |
|---|---|---|
| 1 | `parse_claim` | Read the claim JSON file and return a validated `ClaimInfo` JSON string. |
| 2 | `is_valid_query` | Look up the policy number in a CSV of valid policies; return `True/False` with reason. |
| 3 | `generate_policy_queries` | LLM call that turns claim details into a `PolicyQueries` list of focused KB queries. |
| 4 | `retrieve_policy_text` | Run those queries against ChromaDB and return concatenated relevant policy passages. |
| 5 | `WebSearchTool` | Built-in smolagents tool used to estimate typical real-world repair costs for the damage described. |
| 6 | `generate_recommendation` | LLM call that combines claim info + retrieved policy text into a `PolicyRecommendation`. |
| 7 | `finalize_decision` | Convert the recommendation into a final structured `ClaimDecision`. |

### 6. Prompt Engineering
Four prompt templates wired into `PromptTemplates`:
- **`system_prompt`** — fixes the mandatory 7-step claim-processing order and forbids reordering/skipping.
- **`PlanningPromptTemplate`** — provides initial facts and a step-by-step plan plus update messages.
- **`ManagedAgentPromptTemplate`** — task framing and report formatting.
- **`FinalAnswerPromptTemplate`** — final output template with claim number, coverage, deductible, payout, and notes.

### 7. Agent Assembly
A `ToolCallingAgent` is constructed with all seven tools, the GPT-4o-mini model, `add_base_tools=True`, and the assembled prompt templates.

### 8. Test Runs

| Run | Scenario | Expected Branch |
|---|---|---|
| **Run 1** | Claim with policy number `PL-1` (not in the valid policy CSV). | `is_valid_query` returns False → agent halts early with an invalid-claim decision. |
| **Run 2** | Valid policy number `PN-1`, but absurdly inflated repair cost. | Agent passes validity check, then uses `WebSearchTool` to compare market repair prices and rejects the claim as unrealistic. |
| **Run 3** | Realistic, fully-formed claim. | Claim passes the full pipeline: parse → validate → query generation → policy retrieval → cost sanity check → recommendation → final decision. |

For each run, a claim dictionary is written to a JSON file (`ema.json`, `ema2.json`, `ema3.json`) and passed to `claim_processing_agent.run(...)`.

## Required Inputs

Place these in the working directory before running the notebook:
- `config.json` — contains `API_KEY` and `OPENAI_BASE_URL`.
- `policy.pdf` — the auto insurance policy document used as the RAG knowledge base.
- A CSV of valid policy numbers — consumed by `is_valid_query` to verify claims.

## Key Takeaways

- **Agentic vs. traditional RAG:** instead of one fixed retrieve-then-generate pass, the agent dynamically decides which tool to call next, can short-circuit on invalid input, and can call external tools (web search) mid-flow.
- **Pydantic schemas + structured tools** make the agent's intermediate state inspectable and reduce hallucinated fields.
- **Layered validation** (CSV policy check + market-price web search) catches both clerical fraud and inflated claims before the recommendation stage.

## Future Work (from the notebook)

- Reduce reliance on prompt-only enforcement of the workflow; add guardrails and prompt-injection defenses.
- Add formal RAG evaluation metrics: **Context Precision**, **Context Recall**, **Task Completion**, **Tool Correctness**.
