# What is RAG? (Simplified)

A short guide for anyone new to the idea. No coding experience required.

---

## The problem: smart but out-of-date

You’ve probably used **ChatGPT** or **Gemini**: they’re great at explaining ideas and writing. But ask *“What’s the schedule for this workshop?”* or *“Who are the speakers and what are they covering?”* — and they can’t answer. Why? Because that information lives in *this* event’s materials: the agenda, the speaker list, the PDFs the organizers prepared. None of that was part of the model’s training data.

The model only “knows” what it was trained on. It has no access to the content of **your** session—this workshop, this course, this meeting—unless you give it that content. So if you ask about the current workshop’s schedule or speakers, it may guess or make something up, because that specific information was never in its training set.

**Large language models (LLMs)** are very capable, but they don’t automatically know your session materials, your documents, or your event details. That’s the problem RAG tries to fix.

---

## The idea: give the model the right page

You don’t need to retrain the model. You just need to **find the right pieces of text** from your documents (e.g. the workshop agenda, speaker list) and **hand them to the model** when it answers.

So instead of:

- *“Answer from whatever you remember,”* (e.g. *“What’s the workshop schedule?”*)

you do:

- *“Here are the exact paragraphs that matter—the agenda, the speaker bios. Answer using only these.”*

The model stays the same; what changes is that you **feed it the right context** for each question. That’s the core of RAG.

---

## What does RAG mean?

**RAG** = **R**etrieval **A**ugmented **G**eneration

- **Retrieval** = search your workshop materials (agenda, speaker list, etc.) and get back the most relevant bits.
- **Augmented** = you add that information to the question.
- **Generation** = the model generates an answer (e.g. text).

So: **retrieve** the right text, **add** it to the question, then let the model **generate** the answer. That’s RAG in one sentence.

---

## A simple analogy: textbook and index

Think of a big textbook and its **index** at the back.

1. **Index** = you don’t read the whole book to find “schedule” or “speakers.” You look them up in the index and get page numbers.
2. **You go to those pages** and read the relevant paragraphs.
3. **You answer** the question using only what you read there.

RAG does the same thing, but with:

- Your **workshop materials** (agenda, speaker list, handouts—instead of one textbook),
- A **search system** that finds similar text (instead of a printed index),
- An **AI model** that reads the retrieved text and writes the answer (instead of you).

---

## The five steps (high level)

You can picture the whole process in five steps.

| Step | Name | What happens (in plain English) |
|------|------|---------------------------------|
| **1** | **Your documents** | You have the workshop materials (e.g. agenda, speaker bios, session handouts). This is the “book” the system will search. |
| **2** | **Prepare (ingestion)** | The system cuts the documents into smaller pieces (chunks), turns each piece into a kind of “fingerprint” (embedding), and stores those fingerprints in a search index. This is done once (or when you add new docs). |
| **3** | **You ask a question** | You type a question in normal language, e.g. “What’s the workshop schedule?” or “Who are the speakers?” |
| **4** | **Retrieval** | The system turns your question into the same kind of fingerprint, finds the chunks whose fingerprints are closest to it, and gives you those chunks. So you get “the right pages” for your question. |
| **5** | **Generation** | The model receives your question plus those chunks and writes an answer using *only* that text. So the answer is grounded in your documents. |

So: **documents → prepare once → ask → retrieve the right chunks → model generates the answer.**

---

## Why “chunks” and “embeddings”?

### Why not give the whole document?

Documents can be long. Models have a limit on how much text they can take at once. Also, long texts mix many topics, so the model might get distracted. So we split documents into **chunks** (e.g. a few sentences or a short paragraph). We then search and pass only the **most relevant chunks** to the model.

### What’s an “embedding”?

An **embedding** is a way to turn a piece of text into a list of numbers (a vector). The important part: **similar meanings get similar lists of numbers.** So “workshop schedule” and “session timetable” end up with similar vectors, and the search can find chunks that *mean* something close to the question, not just words that match.

So we:

- Turn each chunk into a vector (embedding),
- Store those vectors in a search index,
- Turn the question into a vector,
- Search for the vectors closest to the question’s vector,
- Return the chunks that produced those vectors.

That’s how we “find the right page” by meaning, not only by keywords.

---

## Picture of the flow

```
  YOU HAVE                    ONE-TIME SETUP
  ┌─────────────┐             ┌──────────────────────────────────┐
  │  Documents  │  ─────────► │  Chunk  →  Embed  →  Search index  │
  │  (.txt etc)│             └──────────────────────────────────┘
  └─────────────┘                              │
                                                │
  YOU ASK A QUESTION                             │
  ┌─────────────┐             ┌─────────────────▼─────────────────┐
  │  "What's    │  ─────────► │  Embed question  →  Search index   │
  │  the refund │             │  → Get top chunks (the "right      │
  │  policy?"   │             │    pages")                         │
  └─────────────┘             └─────────────────┬─────────────────┘
                                                │
                                                ▼
  YOU GET AN ANSWER             ┌──────────────────────────────────┐
  ┌─────────────┐               │  Model reads: question + chunks   │
  │  "According │  ◄─────────── │  Model writes: answer (only from  │
  │  to the     │               │  that context)                    │
  │  policy..." │               └──────────────────────────────────┘
  └─────────────┘
```

---

## Why is this useful?

- **Up-to-date:** Add new documents and re-run the preparation step; the system can answer from the latest info.
- **Your data only:** The model doesn’t need to have seen your notes or policies before; you provide them at answer time.
- **Less guessing:** By insisting “use only this text,” you reduce made-up or off-topic answers.
- **Reusable:** Same idea works for course notes, support docs, internal wikis, etc.

---

## One-sentence summary

**RAG means: when someone asks a question, you search your own documents for the most relevant pieces, then ask an AI to answer using only those pieces—so the answer comes from your content, not from the model’s memory.**

If you’re ready for the technical version (code and pipeline details), see **rag-tutorial-basic.md**.
