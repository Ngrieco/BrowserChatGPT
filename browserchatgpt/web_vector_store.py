from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS, Chroma


class WebVectorStore:
    def __init__(self, pages, lock):
        print("Splitting data.")

        self.lock = lock
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=0)
        self.embeddings = OpenAIEmbeddings()

        docs, metadatas = [], []
        for page in pages:
            splits = self.text_splitter.split_text(page['text'])
            docs.extend(splits)
            metadatas.extend([{"source": page['url']}] * len(splits))

        self.lock.acquire()
        print("acquire")
        self.vector_store = FAISS.from_texts(docs, self.embeddings, metadatas=metadatas)
        print("release")
        self.lock.release()

        print("Successful vector database storage.")

    def add_pages(self, pages):
        docs, metadatas = [], []
        for page in pages:
            splits = self.text_splitter.split_text(page['text'])
            docs.extend(splits)
            metadatas.extend([{"source": page['url']}] * len(splits))


        embeddings = self.embeddings.embed_documents(docs)

        self.lock.acquire()
        #self.vector_store.add_texts(docs, metadatas=metadatas)
        self.vector_store.add_embeddings(zip(docs, embeddings), metadatas=metadatas)
        self.lock.release()

        print("Successful addition to vector database storage.")


if __name__ == "__main__":
    print("Hello world")
    pages = [{"url": "name", "text": "My name is Nick"}]
    vector_store = WebVectorStore(pages)

    pages2 = [{"url": "birthday", "text": "My birthday is March 14th 1995."}]
    vector_store.add_pages(pages2)
    