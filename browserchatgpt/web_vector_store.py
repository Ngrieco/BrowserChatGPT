from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS


class WebVectorStore:
    def __init__(self, pages, lock):
        self.lock = lock
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200, chunk_overlap=0
        )
        self.embeddings = OpenAIEmbeddings()
        self.vector_ids = []

        docs, metadatas = [], []
        for page in pages:
            splits = self.text_splitter.split_text(page["text"])
            docs.extend(splits)
            metadatas.extend([{"source": page["url"]}] * len(splits))

        # Create unique ideas for initial data
        doc_ids = [str(i) for i in range(len(docs))]
        self.vector_ids.extend(doc_ids)

        self.lock.acquire()
        self.faiss = FAISS.from_texts(
            docs, self.embeddings, metadatas=metadatas, ids=doc_ids
        )
        self.lock.release()

    def add_pages(self, pages):
        docs, metadatas = [], []
        for page in pages:
            splits = self.text_splitter.split_text(page["text"])
            docs.extend(splits)
            metadatas.extend([{"source": page["url"]}] * len(splits))

        # Create unique ids for new data
        self.lock.acquire()
        num_curr_ids = len(self.vector_ids)
        num_new_ids = len(docs)
        doc_ids = [str(i) for i in range(num_curr_ids, num_curr_ids + num_new_ids)]
        self.vector_ids.extend(doc_ids)
        self.lock.release()

        embeddings = self.embeddings.embed_documents(docs)

        if len(docs) == len(embeddings) and len(docs) > 0:
            self.lock.acquire()
            self.faiss.add_embeddings(
                zip(docs, embeddings), metadatas=metadatas, ids=doc_ids
            )
            self.lock.release()

        return embeddings

    def reset(self):
        if len(self.vector_ids) > 0:
            self.faiss.delete(self.vector_ids)
            self.vector_ids = []


if __name__ == "__main__":
    print("Hello world")
    pages = [{"url": "name", "text": "My name is Nick"}]
    vector_store = WebVectorStore(pages)

    pages2 = [{"url": "birthday", "text": "My birthday is March 14th 1995."}]
    vector_store.add_pages(pages2)
