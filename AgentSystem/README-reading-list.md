# Reading List: AI & LLMs — Quick Reference Summaries

A curated set of resources covering AI tools, foundational research, and the current LLM landscape.

---

## 1. Claude Code for Everyone
**Source:** [gexijin.github.io/vibe](https://gexijin.github.io/vibe/)

A step-by-step tutorial site for getting started with Claude Code — Anthropic's AI coding assistant that runs locally in your terminal. The site covers installation on Windows and Mac, connecting VS Code, adding version control with Git, and working with R and Python. It progresses from basic setup through advanced topics like Docker environments, custom slash commands, building Claude "skills", and creating AI agents. Requires a paid Claude subscription or an OpenRouter API key as an alternative.

**Best for:** Complete beginners who want guided, hands-on practice with Claude Code from scratch.

---

## 2. What Is Prompt Engineering?
**Source:** [Google Cloud](https://cloud.google.com/discover/what-is-prompt-engineering?hl=en)

An overview of prompt engineering — the practice of crafting effective inputs to guide AI language models toward desired outputs. Covers the key building blocks of good prompts (format, context, examples, and multi-turn design), the main prompt types (zero-shot, few-shot, and chain-of-thought), and practical use cases across writing, translation, Q&A, summarization, and code generation. Also touches on fine-tuning and adapting prompts based on model feedback.

**Best for:** Anyone new to working with LLMs who wants a structured introduction to getting better results.

---

## 3. Attention Is All You Need (2017)
**Source:** [arxiv.org/pdf/1706.03762](https://arxiv.org/pdf/1706.03762) — Vaswani et al., Google Brain

The landmark paper that introduced the **Transformer architecture**, which underpins virtually every modern LLM. The core idea: replace the recurrent neural networks (RNNs) that dominated sequence modeling with a mechanism called **self-attention**, which can relate any two positions in a sequence directly regardless of distance. This makes training massively more parallelizable and dramatically faster. On machine translation benchmarks at the time, the Transformer outperformed all prior approaches at a fraction of the training cost.

**Best for:** Understanding the foundational architecture behind GPT, Claude, Gemini, and almost every other modern AI model.

---

## 4. Dissociating Language and Thought in LLMs (2023)
**Source:** [arxiv.org/pdf/2301.06627](https://arxiv.org/pdf/2301.06627) — Mahowald, Ivanova et al., MIT / UT Austin

A research paper arguing that being good at language and being good at thinking are two distinct capabilities — and that current LLMs excel at one but not the other. The authors distinguish between **formal linguistic competence** (grammar, fluency, pattern-matching) and **functional linguistic competence** (real-world reasoning, commonsense, goal-directed communication). LLMs score near-human on formal tasks but remain inconsistent on functional ones. The paper cautions against assuming that fluent text generation implies genuine understanding or intelligence.

**Best for:** Anyone who wants a grounded, nuanced view of what LLMs actually can and cannot do — and why.

---

## 5. Top LLMs to Use in 2026 (Creole Studios)
**Source:** [creolestudios.com/top-llms](https://www.creolestudios.com/top-llms/)

A practitioner-focused breakdown of the leading LLMs as of 2026, organized by use case rather than by hype. Key picks: GPT-5 for general reasoning and production use, DeepSeek R1 for math and complex logic, Claude Sonnet 4.5 for coding and debugging, Gemini 2.5 Flash for high-volume low-latency tasks, and Llama 4 Scout for private/open-source deployment. The central argument: there is no single best model anymore — only the best model for your specific workload. Open-source models are rapidly closing the gap with proprietary ones.

**Best for:** Engineers and product teams deciding which model to use for a specific task.

---

## 6. Top 9 Large Language Models — March 2026 (Shakudo)
**Source:** [shakudo.io/blog/top-9-large-language-models](https://www.shakudo.io/blog/top-9-large-language-models)

An enterprise-oriented survey of the top LLMs as of early 2026, evaluated across reasoning quality, multimodal capability, latency, cost, and deployment flexibility. The guide emphasizes that modern teams must weigh tradeoffs across proprietary vs. open-weight models, cloud vs. on-premise deployment, and speed vs. depth of reasoning. Key evaluation criteria include step-by-step logical decomposition, cross-modal understanding (text, images, audio, video), and stability under long prompts.

**Best for:** Enterprise teams evaluating which LLMs to integrate into production data stacks or AI pipelines.

---

## Quick Comparison

| Resource | Type | Level | Key Takeaway |
|----------|------|-------|--------------|
| Claude Code for Everyone | Tutorial site | Beginner | Hands-on path from zero to agentic coding |
| Google Cloud: Prompt Engineering | Guide | Beginner | How to write better prompts |
| Attention Is All You Need | Research paper | Technical | Transformers replaced RNNs and changed everything |
| Dissociating Language and Thought | Research paper | Intermediate | LLMs are fluent but not necessarily intelligent |
| Creole Studios: Top LLMs 2026 | Comparison guide | Intermediate | Pick the right model for your specific job |
| Shakudo: Top 9 LLMs | Enterprise guide | Intermediate | Evaluate LLMs across reasoning, cost, and deployment |
