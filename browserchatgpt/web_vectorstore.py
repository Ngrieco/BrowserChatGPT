from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS, Chroma


class WebVectorStore:
    def __init__(self, data):
        documents = [
            Document(page_content=text, metadata={"source": "local"})
            for text in data
        ]

        text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
        documents = text_splitter.split_documents(documents)

        embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma.from_documents(documents, embeddings)


"""
class WebVectorStore:
    def __init__(self, pages):
        print("Splitting data.")
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

        docs, metadatas = [], []
        for page in pages:
            splits = text_splitter.split_text(page['text'])
            docs.extend(splits)
            metadatas.extend([{"source": page['url']}] * len(splits))


        embeddings = OpenAIEmbeddings()
        self.vector_store = FAISS.from_texts(docs, embeddings, metadatas=metadatas)
        print("Successful vector database storage.")
"""
