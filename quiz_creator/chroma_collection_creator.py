import streamlit as st
from document_processor import DocumentProcessor
from embedding_client import EmbeddingClient


# Import Task libraries
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma

class ChromaCollectionCreator:
    def __init__(self, processor, embed_model):
        self.processor = processor      # This will hold the DocumentProcessor
        self.embed_model = embed_model  # This will hold the EmbeddingClient
        self.db = None                  # This will hold the Chroma collection
    
    def create_chroma_collection(self):
        if len(self.processor.pages) == 0:
            st.error("No documents found!", icon="🚨")
            return
        
        text_splitter = CharacterTextSplitter(
                separator="\n\n",
                chunk_size=1024,
                chunk_overlap=256,
                length_function=len,
                is_separator_regex=False,
            )
       
        texts = text_splitter.split_documents(self.processor.pages)
        if texts is not None:
            st.success(f"Successfully split pages to {len(texts)} documents!", icon="✅")

        self.db = Chroma.from_documents(texts, self.embed_model)
        
        if self.db:
            st.success("Successfully created Chroma Collection!", icon="✅")
        else:
            st.error("Failed to create Chroma Collection!", icon="🚨")
    
    def query_chroma_collection(self, query) -> Document:
        if self.db:
            docs = self.db.similarity_search_with_relevance_scores(query)
            if docs:
                return docs[0]
            else:
                st.error("No matching documents found!", icon="🚨")
        else:
            st.error("Chroma Collection has not been created!", icon="🚨")
    
    def as_retriever(self):
        return self.db.as_retriever()