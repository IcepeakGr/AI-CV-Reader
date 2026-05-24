# This is a simple implementation of a Retrieval-Augmented Generation (RAG) engine using LangChain and OllamaLLM. 
# The RAG engine retrieves relevant documents based on a query and then generates a response using the retrieved documents.

import os

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import VectorDB

class RagEngine:
    def __init__(self):

        self.model = OllamaLLM(model="llama3.2", base_url=os.getenv("OLLAMA_BASE_URL")) # Use host.docker.internal to access the Ollama server running on the host machine from within the Docker container.

        self.vector_db = VectorDB()

        # self.prompt_template = """You are an expert Resume Analyst. Answer the question based ONLY on the provided context.
        # RULES:
        # - Keep information from different files strictly separated.
        # - Do NOT organize the skills by file name (e.g., Never write "FILE: filename.pdf").
        # - Extract EVERY SINGLE relevant fact, skill, tool, framework, or experience mentioned in the context. Do not summarize or omit anything.
        # - State exactly which file each fact comes from.
        # - If a fact or skill appears in multiple files, list it under each respective file's section.
        # - Only cite a source if the text is explicitly contained within that specific file's context. If unsure, do not guess the filename.
        
        # Context:
        # {context}

        # Question:
        # {question}
        # """

        self.prompt_template = """You are an expert Resume Analyst. Answer the question based ONLY on the provided context.
        RULES:
        - Create a single, unified, and consolidated response. Do NOT separate the output into different file sections or headers.
        - Extract EVERY SINGLE relevant fact, skill, tool, framework, or experience mentioned across all documents. Do not summarize or omit anything.
        - Merge duplicate skills or experiences together into clean, comprehensive markdown bullet points.
        - Do NOT print internal file metadata, formatting tags, or text like "FILE: filename.pdf".
        
        Context:
        {context}

        Question:
        {question}
        """

        # Create a chat prompt template using the defined prompt template
        self.prompt = ChatPromptTemplate.from_template(self.prompt_template)

        # Create a chain that combines the prompt and the model using pipe.
        self.chain = self.prompt | self.model 


    def ask(self, question):

        # Get the retriever from the vector database.
        retriever = self.vector_db.get_retriever() 

        # Use the retriever to get the relevant context for the question.
        context = retriever.invoke(question)
        context_text = "\n\n--- NEW DATA SECTION ---\n\n".join([con.page_content for con in context])

        # Use the chain to generate a response based on the context and question.
        result = self.chain.invoke({"context": context_text, "question": question})

        
        return result 

# This loop is for TESTING the RAG engine. 
# The real implementation will be in the Streamlit app.
# It allows the user to ask questions and get answers based on the retrieved context from the vector store.

# Infinite Loop to ask the questions. Terminates with 'q'
# while True:
#     print("\n\n-------------------------------")
#     question = input("Ask your question (q to quit): ")
#     print("\n\n")
    
#     if question == "q":
#         break

#     vector_db = VectorDB() # Create an instance of the VectorDB class to access the vector store and retriever.
#     context = vector_db.get_retriever().invoke(question) # Use the retriever to get the relevant context for the question.
#     result = chain.invoke({"context": context, "question": question}) # Use the chain to generate a response based on the context and question.
#     print(f"Answer: {result}") # Print the generated answer.