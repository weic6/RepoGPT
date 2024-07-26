__import__("pysqlite3")
import sys

# import pysqlite3

sys.modules["sqlite3"] = sys.modules["pysqlite3"]

import os
import shutil
from crawl import *
from langchain_community.vectorstores.chroma import Chroma
from langchain.document_loaders import NotebookLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings


def get_vectordb_v3(openai_api_key, repo_path, persist_directory=None):
    """
    docs contain meta data
    """
    if persist_directory is None:
        persist_directory = os.path.join(repo_path, "_chroma")

    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)  # remove the directory and its contents

    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)

    file_paths = crawl_local_repo(repo_path)
    documents = [
        Document(
            page_content=read_file_content(path),
            metadata={"source": path},
        )
        for path in file_paths
        if read_file_content(path)
    ]

    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embedding,
        persist_directory=persist_directory,
    )
    vectordb.persist()
    return vectordb


def get_vectordb(openai_api_key, repo_path, persist_directory=None):
    if persist_directory is None:
        persist_directory = os.path.join(repo_path, "_chroma")

    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)  # remove the directory and its contents

    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
    docs = load_docs_in_repo(repo_path)
    split_docs = split_docs(docs)  # ???: can GPT know file source?

    vectordb = Chroma.from_documents(
        documents=split_docs,
        embedding=embedding,
        persist_directory=persist_directory,
    )
    vectordb.persist()

    return vectordb


def load_vector_db(openai_api_key, persist_directory=None):
    if not os.path.exists(persist_directory):
        print(f"Persist directory {persist_directory} does not exist.")
        return None

    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding,
    )
    return vectordb


def split_docs(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    docs_split = text_splitter.split_documents(docs)
    return docs_split


def load_docs_in_repo(repo_path):
    """
    TODO: add more specific loaders?
    """
    docs = []
    files = crawl_local_repo(repo_path)
    for file in files:
        try:
            if file.endswith(".ipynb"):
                loader = NotebookLoader(file)
            else:
                loader = TextLoader(file, encoding="utf-8")
                docs.extend(loader.load_and_split())
        except Exception as e:
            pass

    return docs


def read_file_content(path):
    pass
