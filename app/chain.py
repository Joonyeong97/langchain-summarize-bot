from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders.pdf import *
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.callbacks.manager import AsyncCallbackManager
import os

model_name = os.environ.get('MODEL_NAME', "gpt-3.5-turbo")

def get_pdf_docs(text: str, is_local: bool):
    if is_local:
        loader = PyPDFLoader(text)
    else:
        loader = OnlinePDFLoader(text)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    return docs


def get_chain(summarize_handler):
    manager = AsyncCallbackManager([])
    summarize_manager = AsyncCallbackManager([summarize_handler])
    chat = ChatOpenAI(model_name=model_name, callback_manager=summarize_manager)

    chain = load_summarize_chain(llm=chat, chain_type="map_reduce", verbose=True, callback_manager=manager)
    chain.llm_chain.prompt.template = chain.llm_chain.prompt.template.replace("CONCISE SUMMARY:", "CONCISE SUMMARY IN KOREAN:")

    return chain