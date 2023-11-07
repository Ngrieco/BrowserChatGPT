from browserchatgpt.web_llm import WebLLM
from browserchatgpt.web_vector_store import WebVectorStore

pages = [{"url": "name", "text": "My name is Nick"}]
vector_store = WebVectorStore(pages)
llm = WebLLM(vector_store)

query = "What's my name?"
result = llm.query(query)
print("AI: ", result)

query = "Whens my birthday?"
result = llm.query(query)
print("AI: ", result)

pages2 = [{"url": "birthday", "text": "My birthday is March 14th 1995."}]
vector_store.add_pages(pages2)

query = "Whens my birthday?"
result = llm.query(query)
print("AI: ", result)
