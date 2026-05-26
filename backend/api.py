import shutil
import uvicorn
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel, Field
from rag_engine import RagEngine
from vector import VectorDB
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

# Prewarming the RAG engine and vector database at startup to ensure they're ready to handle requests immediately when the API starts.
# Lifespan function to initialize the RAG engine and vector database at startup
# This ensures that the potentially time-consuming initialization process of loading the vector store and setting up the RAG engine happens only once at startup, rather than on the first request, 
# which can lead to a better user experience with faster response times for the initial requests.
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI is starting up... Initializing RAG engine and vector database.")
    try:
        global rag_engine
        global vector_db

        vector_db = VectorDB()  
        vector_db.load_vector_store()  

        rag_engine = RagEngine()  

        print("Initialization complete. FastAPI is ready to handle requests.")
        yield
    except Exception as e:
        print(f"Error during initialization: {e}")
        raise e  # Reraise the exception to prevent the app from starting if initialization fails
    
    
app = FastAPI(lifespan=lifespan)
rag_engine = RagEngine()
vector_db = VectorDB()

# API Base Models

# ChatRequest model for handling incoming chat requests
class ChatRequest(BaseModel):
    question: str

# ChatResponse model for structuring the response from the user input
class ChatResponse(BaseModel):
    answer: str

# UploadResponse model for structuring the response after a file upload
class UploadResponse(BaseModel):
    message: str




# API Endpoints

# The /chat endpoint receives a question from the user, processes it through the RAG engine, and returns an answer 
# based on the retrieved context from the vector database.
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        answer = rag_engine.ask(request.question)
        return ChatResponse(answer=answer)
    except Exception as e:
        print(f"RagEngine Error: {e}")
        raise HTTPException(status_code=500, detail="RagEngine error: " + str(e))


# The /upload endpoint allows users to upload documents (PDF, DOCX, TXT) which are then saved to a specified location 
# (in our case, the 'documents' folder) and indexed in the vector database for future retrieval.
@app.post("/upload")
def upload_and_index_document(files: List[UploadFile] = File(...)):

    allowed_extensions = ['pdf', 'docx', 'txt']
    upload_count = 0
    try:
        for file in files:
            file_extension = file.filename.lower().split('.')[-1]

            if file_extension not in allowed_extensions:
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not supported.")
            
            file_location = vector_db.get_data_folder() + "/" + file.filename


            # Save the uploaded file to the specified location
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            upload_count += 1

        # After saving the files, we reload the vector store for the new documents to appear.
        vector_db.load_vector_store()
        return UploadResponse(message=f"{upload_count} file(s) uploaded and indexed successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="File upload error: " + str(e))

# @app.delete("/reset")
# def reset_vector_db():
#     try:
#         vector_db.reset_vector_store()
#         return {"message": "Vector database reset successfully."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Error resetting vector database: " + str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
            
    
       
