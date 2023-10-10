from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma


class WebData:
    def __init__(self, data):
        # data - list of string where each string is a
        # loader = TextLoader("./state_of_the_union.txt")
        # documents = loader.load()
        # loaders = [....]
        # docs = []
        # for loader in loaders:
        #     docs.extend(loader.load())
        # print(data)
        documents = [
            Document(page_content=text, metadata={"source": "local"}) for text in data
        ]

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        documents = text_splitter.split_documents(documents)

        embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma.from_documents(documents, embeddings)
