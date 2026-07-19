import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter

class RAGSystem:
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
    def _initialize_collection(self, collection_name: str, file_path: str, headers_to_split_on: list):
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        docs = markdown_splitter.split_text(content)
        
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=collection_name
        )
        return vectorstore

    def get_style_retriever(self):
        # We assume collections are already created or we create them on the fly if not existing
        # But for this simple implementation, we can just load or recreate
        headers_to_split_on = [
            ("#", "Style Name")
        ]
        vs = self._initialize_collection("style_guides", "rag_docs/style_guides.md", headers_to_split_on)
        if not vs:
            vs = Chroma(collection_name="style_guides", embedding_function=self.embeddings, persist_directory=self.persist_directory)
        return vs.as_retriever(search_kwargs={"k": 2})

    def get_api_retriever(self):
        headers_to_split_on = [
            ("#", "API Feature")
        ]
        vs = self._initialize_collection("remotion_snippets", "rag_docs/remotion_snippets.md", headers_to_split_on)
        if not vs:
            vs = Chroma(collection_name="remotion_snippets", embedding_function=self.embeddings, persist_directory=self.persist_directory)
        return vs.as_retriever(search_kwargs={"k": 3})
