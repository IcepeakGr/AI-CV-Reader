
import shutil

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader, Docx2txtLoader, PyMuPDFLoader
import os
import uuid
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Load environment variables from .env file
load_dotenv()

class VectorDB:
    def __init__(self):
        self.db_location = os.getenv("DB_LOCATION")
        self.data_folder = os.getenv("DATA_FOLDER")
        self.collection_name = os.getenv("COLLECTION_NAME")

        self.embeddings_model = OllamaEmbeddings(model="nomic-embed-text", base_url=os.getenv("OLLAMA_BASE_URL"))

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200
        )



    # Load documents from the specified location and create a Chroma vector store
    def load_documents(self):
        documents_in_chunks = []
        ids = []
        loader = None

        for file in os.listdir(self.data_folder):
            if file.lower().endswith(".pdf"):
                loader = PyMuPDFLoader(os.path.join(self.data_folder, file))

            elif file.lower().endswith(".txt"):
                loader = TextLoader(os.path.join(self.data_folder, file), encoding="utf-8")

            elif file.lower().endswith(".docx"):
                loader = Docx2txtLoader(os.path.join(self.data_folder, file))

            else:
                print(f"Unsupported file format (PDF, TXT, DOCX): {file}")
                continue
        
            if loader:
                loaded_docs = loader.load()

                for doc in loaded_docs:
                    # We use a very distinct "Header" for every single chunk
                    doc.metadata["source"] = file
                    doc.page_content = f"FILE: {file}\n{doc.page_content}"
                #     #doc.page_content = f"--- DOCUMENT: {file} ---\n{doc.page_content}\n--- END OF {file} ---"

                #     # Cleaning the file for the splitter
                #     doc.page_content = doc.page_content.strip()

                #     # Print the first 500 characters of the loaded document for debugging
                #     print(f"Loaded document: {file} - First 500 characters:\n{doc.page_content[:500]}\n")

                chunks = self.splitter.split_documents(loaded_docs)

                # Add the filename as metadata to each chunk
                for chunk in chunks:
                    chunk.metadata["source"] = file
                    chunk.page_content = f"FILE: {file}\n{chunk.page_content}"

                print(f"File: {file} - Chunks created: {len(chunks)}")
                documents_in_chunks.extend(chunks)

            print(f"Loaded and split document: {file}")
        

        # Generate unique IDs for each document chunk
        ids = [str(uuid.uuid4()) for _ in range(len(documents_in_chunks))]


        return documents_in_chunks, ids
        

    # def reset_vector_store(self):
    #     try:
    #         if os.path.exists(self.db_location):
              
    #             # Remove the existing vector store directory and all its contents
    #             shutil.rmtree(self.db_location)
    #             print(f"Successfully deleted directory: {self.db_location}")
    #         else:
    #             print("Vector store directory does not exist. Creating a fresh one.")

    #         # Recreate the directory after deletion
    #         #os.makedirs(self.db_location, exist_ok=True)

    #     except Exception as e:
    #         print(f"Error during vector store reset: {e}")

    #    # After resetting, we load a fresh, empty vector store to ensure the system is ready for new documents to be added.
    #     print("Reloading a fresh, empty vector store...")
    #     self.load_vector_store()

    
    # Load the vector store from the specified location. 
    # If it doesn't exist, create a new one using the loaded documents and embeddings model.
    def load_vector_store(self):

        # We check if the vector store already exists at the specified location. If it does, we load it directly.
        sqlite_file = os.path.join(self.db_location, "chroma.sqlite3")

        # Check if the vector store already exists at the specified location
        if os.path.exists(sqlite_file):
            print("Vector store found. Loading existing vector store...")
            vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings_model,
                persist_directory=self.db_location
            )
            print("Vector store loaded successfully.")
            return vector_store

        documents, ids = self.load_documents()

        if not documents:
            print("No documents found in the specified location.")
            return None

        vector_store = Chroma.from_documents(
            documents=documents,
            ids=ids,
            collection_name=self.collection_name,
            embedding=self.embeddings_model,
            persist_directory=self.db_location
        )

        print("Vector store loaded successfully.")
        return vector_store
    

    # Get a retriever from the vector store that can be used to retrieve relevant documents based on a query. 
    # The retriever is configured to return the top 1 most relevant document.
    def get_retriever(self):

        vector_store = self.load_vector_store()

        if vector_store is None:
            print("Retriever cannot be created yet: Vector store is empty.")
            return None

        retriever = vector_store.as_retriever(search_kwargs={"k": 7})

        print("Retriever created successfully.")
        return retriever
    


    # Helper methods
    def get_data_folder(self):
        return self.data_folder
    
    def get_db_location(self):
        return self.db_location

        
