# RAG Architecture (Retrieval-Augmented Generation)

## What is an Embedding?
An embedding is a way of translating text into a list of numbers (a "vector") so that a computer can understand its meaning. Words or sentences with similar meanings will have similar numbers. For example, "Software Engineer" and "Developer" will have embeddings that are mathematically close to each other, even though the letters are completely different.

## What is Vector Search?
Vector search is the process of comparing these mathematical vectors to find which ones are closest to each other. When a user asks a question, we convert their question into a vector and use a mathematical formula (like cosine similarity) to find documents in our database that have the most similar vectors. This allows us to search by *meaning* rather than exact keyword matches.

## What is pgvector?
`pgvector` is an extension for PostgreSQL that allows it to store and quickly search through vector embeddings directly in the database. Instead of exporting data to a separate specialized vector database (like Pinecone or Milvus), `pgvector` lets us keep our relational data (users, resumes, jobs) and vector data in the exact same place.

## What is RAG?
RAG stands for Retrieval-Augmented Generation. Large Language Models (like Gemini or ChatGPT) are trained on massive amounts of data, but they don't know your specific, private data (like a user's uploaded resume).
RAG solves this by:
1. **Retrieving** relevant information from a database (using vector search).
2. **Augmenting** (adding) that retrieved context to the prompt.
3. Asking the LLM to **Generate** an answer based *only* on that context.

## Why use RAG?
Without RAG, an AI might hallucinate (make up facts) because it tries to guess the answer. With RAG, we provide the exact facts to the AI inside the prompt, effectively giving it an "open-book test." This makes the AI's answers significantly more accurate, personalized, and grounded in reality.

## How does retrieval work in CareerForge AI?
1. When a user uploads a resume or job description, we split the text into small "chunks."
2. We send each chunk to the Gemini Embeddings API (`models/text-embedding-004`), which returns a 768-dimensional vector.
3. We store the text chunk and its vector in our PostgreSQL database using `pgvector`.
4. When we need to generate an interview question or evaluate an answer, we turn the user's current context into a vector.
5. We search the database for the top 3 most mathematically similar chunks.
6. We inject those chunks into the Gemini prompt as `<RETRIEVED_CONTEXT>`.

## How does RAG help reduce hallucinations?
In our prompt templates (e.g., `interviewer.py`), we explicitly instruct the AI:
> "Ground your evaluation using the `<RETRIEVED_CONTEXT>`. Do NOT invent facts, skills, or projects. If information isn't available, output 'Not found in the provided information'."
Because the AI has the exact textual facts right in front of it, it relies on that data rather than guessing.
