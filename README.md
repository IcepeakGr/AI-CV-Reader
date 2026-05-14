# CV Reader Assistant

>This project is a small Retrieval-Augmented Generation (RAG) application that allows users to upload documents (for example CVs) and ask questions about them in natural language.

The goal of the project is to demonstrate how an **LLM can retrieve information** from uploaded documents instead of relying only on its own knowledge.

The system reads documents, indexes them in a vector database, and then uses a language model to answer questions based only on the content of those documents.


## How Does The Pipeline Work ?

The pipeline works roughly like this:

### 1. Document Upload

Users upload documents from the Streamlit interface.
The files are sent to the FastAPI Back End and saved in the data folder.

Supported formats:

- PDF
- TXT
- DOCX



### 2. Document Loading

The Back End scans the data folder and loads each document using the appropriate loader.

Examples:

**PyMuPDFLoader** for PDFs
**TextLoader** for text files
**Docx2txtLoader** for Word documents

Each document is also tagged with metadata that stores the original filename.



### 3. Chunking

Large documents are split into smaller pieces, called **chunks**.

This is necessary because LLMs work best when the context is not too large.

Each chunk keeps the metadata of the original document so we always know where the information came from.



### 4. Embedding and Indexing

Each chunk is converted into a vector embedding using the embedding model:

>nomic-embed-text

These embeddings are stored in **ChromaDB**, which allows the system to perform semantic search over the documents.

This means the system can retrieve relevant text even if the user's question does not exactly match the wording in the document.


### 5. Retrieving Relevant Context

When the user asks a question, the system:

- Converts the question into an embedding
- Searches the vector database
- Retrieves the most relevant chunks

In this project, the retriever uses **MMR (Maximal Marginal Relevance)** to return diverse and relevant results.



### 6. Generating the Answer

The retrieved chunks are combined into a context block and passed to the LLM together with the user's question.



***


## Technologies Used in the Project

### FastAPI

**FastAPI** is used to build the backend API.

The backend exposes two main endpoints:

- /upload to handle document uploads and indexing
- /chat to recieve user questions and returns answers from the RAG engine

FastAPI was chosen because it is lightweight, easy to set up, and integrates well with Python-based AI pipelines.



### Streamlit

**Streamlit** is used for the frontend interface.

It provides:

- A simple chat interface for asking questions
- A sidebar for uploading documents
- Real-time interaction with the backend API

The Streamlit app sends requests to the FastAPI backend using HTTP requests.



### LangChain

**LangChain** is used to build the RAG pipeline.

In this project it is responsible for:

- Loading documents
- Splitting them into chunks
- Managing the prompt template
- Connecting the retriever with the LLM

LangChain is one of the best AI Frameworks to connect all the different components of a RAG system.



### LangChain Document Loaders

Different **Loaders** are used depending on the document format:

**PyMuPDFLoader** for PDFs
**TextLoader** for text files
**Docx2txtLoader** for Word documents

This allows the system to support multiple document types without changing the indexing pipeline.



### ChromaDB

**ChromaDB** is used as the Vector Database.

It stores **embeddings** of document chunks and allows the system to perform similarity search when a user asks a question.

When a query is received, Chroma retrieves the most relevant chunks which are then passed to the Language Model as context.



### Ollama

**Ollama** is used to run models locally.

Two models are used in this project:

> nomic-embed-text

> llama3.2

Running the models locally makes the system independent from external APIs and maintains privacy and security.



***



## A Few Words

Thank you for reaching this far.
This was my first project building an AI agent using a **Retrieval-Augmented Generation (RAG)** pipeline.

I built it mainly to better understand how modern LLM systems retrieve and reason over documents instead of relying only on pre-trained knowledge.

I really enjoyed working on it and experimenting with the different components of the system.