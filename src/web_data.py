from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma


class WebData:
    def __init__(self, data):
        documents = [
            Document(page_content=text, metadata={"source": "local"})
            for text in data
        ]

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        documents = text_splitter.split_documents(documents)

        embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma.from_documents(documents, embeddings)
