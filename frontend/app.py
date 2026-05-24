# This is the frontend Streamlit app that interacts with the RAG engine and the FastAPI backend.


import requests
import streamlit as st

st.set_page_config(page_title="CV Reader Assistant - PlanB Project")
st.title("CV Reader Assistant")



# Sidebar for uploading documents to the vector store. 
# It allows users to upload multiple files and sends them to the FastAPI backend 
# for processing and indexing in the vector store.
with st.sidebar:
    st.header("Upload Documents")
    uploaded_files = st.file_uploader("Select CVs", accept_multiple_files=True)
    if st.button("Process Documents"):
        if uploaded_files:
            # Prepare files for FastAPI
            files = [("files", (f.name, f.getvalue())) for f in uploaded_files]
            # Send to FastAPI
            response = requests.post("http://backend:8000/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                st.success(data.get("message", "Success, but 'message' key was missing!"))
            else:
                st.error(f"Error {response.status_code}: {response.json()}")
    
    # Button to reset the vector database. This will send a request to the FastAPI backend to wipe the existing vector store clean and re-initialize it.
    # if st.button("Reset Vector Database", type="secondary", help="Wipes the entire database clean"):
    #     with st.spinner("Wiping vector store..."):
    #         try:
    #             # Send the delete/reset command to your FastAPI backend
    #             response = requests.delete("http://backend:8000/reset")
                
    #             if response.status_code == 200:
    #                 st.session_state.upload_success_msg = "Database successfully wiped and re-initialized!"
    #                 # Force a reset of the file uploader key too
    #                 st.session_state.uploader_key += 1
    #                 st.rerun()
    #             else:
    #                 st.error(f"Failed to reset: {response.json().get('detail', 'Unknown error')}")
    #         except Exception as e:
    #             st.error(f"Could not connect to backend to reset: {e}")
                
# Show the User Interface for asking questions to the RAG engine.
def show_ui(prompt_to_user="Ask me anything.."):
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": prompt_to_user}]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User-provided prompt
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    
    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                payload = {"question": prompt}
                response = requests.post("http://backend:8000/chat", json=payload)
                
                if response.status_code == 200:
                    ans_text = response.json()["answer"]
                    st.markdown(ans_text)
                    st.session_state.messages.append({"role": "assistant", "content": ans_text})
                else:
                    st.error("API error.")


if __name__ == "__main__":
    show_ui()