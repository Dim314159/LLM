import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
import os
import tempfile
import uuid

class DocumentProcessor:
    def __init__(self):
        self.pages = [] 
    
    def ingest_documents(self):
        uploaded_files = st.file_uploader(
            label = 'Choose PDF files',
            type = 'pdf',
            accept_multiple_files = True
        )
        
        if uploaded_files is not None:
            for uploaded_file in uploaded_files:
                # Generate a unique identifier to append to the file's original name
                unique_id = uuid.uuid4().hex
                original_name, file_extension = os.path.splitext(uploaded_file.name)
                temp_file_name = f"{original_name}_{unique_id}{file_extension}"
                temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)

                # Write the uploaded PDF to a temporary file
                with open(temp_file_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())

                loader = PyPDFLoader(temp_file_path)
                pages = loader.load_and_split()
                self.pages.extend(pages)
                
                os.unlink(temp_file_path)
            
            # Display the total number of pages processed.
            st.write(f"Total pages processed: {len(self.pages)}")