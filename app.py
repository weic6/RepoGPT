__import__("pysqlite3")
import pysqlite3
import sys

sys.modules["sqlite3"] = sys.modules["pysqlite3"]
import chromadb
import streamlit as st
import os
from crawl import *
from db import *
from llm import *
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

github_token = os.getenv("GITHUB_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")
# persist_directory = os.getenv("CHROMA_DIR")


def main():
    st.title("RepoGPT")
    default_api_key = os.getenv("OPENAI_API_KEY")
    default_github_token = os.getenv("GITHUB_TOKEN")
    openai_api_key = st.sidebar.text_input(
        "OpenAI API Key", type="password", value=default_api_key
    )
    github_token = st.sidebar.text_input(
        "GitHub Token", type="password", value=default_github_token
    )

    gpt_model = st.sidebar.radio(
        "Select gpt model:",
        ["gpt-4o", "gpt-3.5-turbo"],
        index=0,  # default choice is gpt+RAG+memory
    )

    selected_mode = st.sidebar.radio(
        "Select mode:",
        ["gpt", "gpt+RAG", "gpt+RAG+memory"],
        index=2,  # default choice is gpt+RAG+memory
        captions=[
            "Chat with GPT",
            "Chat with GPT and RAG",
            "Chat with GPT, RAG and Memory",
        ],
    )
    # example_repo_path = "/home/dtvi/Documents/wei/RepoGPT"
    example_repo_path = (
        "/home/dtvi/projects/repository/mtl-dpdk/Media-Transport-Library"
    )
    repo_path = st.sidebar.text_input(
        "Enter your local repository path...",
        value=example_repo_path,
    )
    if not repo_path:
        st.warning("Please enter local repository path.")
        return

    # owner, repo = extract_owner_repo(repo_path)
    # st.sidebar.write(f"Owner: {owner}, Repo: {repo}")
    # file_paths = crawl_repo(owner, repo, github_token)

    file_paths = crawl_local_repo(repo_path, rel_path=True)

    st.sidebar.write(f"Found {len(file_paths)} files.")

    if st.sidebar.button("List All Files"):
        if "show_files" not in st.session_state:
            st.session_state["show_files"] = True
        else:
            st.session_state["show_files"] = not st.session_state["show_files"]
    if st.session_state.get("show_files", False):
        for file_path in file_paths:
            # st.sidebar.write(f"https://github.com/{owner}/{repo}/blob/main/{file_path}")
            st.sidebar.write(file_path)

    if st.sidebar.button("Select persist chroma db"):
        if persist_directory := st.sidebar.text_input("Directory to chroma db"):
            st.session_state["persist_directory"] = persist_directory
            vectordb = load_vector_db(
                openai_api_key,
                st.session_state["persist_directory"],
            )
            st.sidebar.write("Chroma db loaded successfully!")
            st.session_state["vectordb"] = vectordb
    elif st.sidebar.button("Create persist chroma db"):
        st.session_state["persist_directory"] = os.path.join(repo_path, "_chroma")
        st.sidebar.write("Vectorizing the documents...")
        vectordb = get_vectordb(
            openai_api_key,
            repo_path,
            st.session_state["persist_directory"],
        )
        st.sidebar.write("Chroma db created successfully!")
        st.session_state["vectordb"] = vectordb

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Chat with repoGPT"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # add user's input to conversation history
        st.session_state.messages.append({"role": "user", "content": prompt})

        if selected_mode == "gpt":
            answer = generate_response(prompt, gpt_model, openai_api_key)
        elif selected_mode in ["gpt+RAG", "gpt+RAG+memory"]:
            if "vectordb" not in st.session_state:
                st.error("Please confirm vectorization before using this mode.")
                return
            vectordb = st.session_state["vectordb"]
            if selected_mode == "gpt+RAG":
                answer = get_qa_chain(prompt, gpt_model, openai_api_key, vectordb)
            else:
                answer = get_chat_qa_chain(prompt, gpt_model, openai_api_key, vectordb)

        if answer is not None:
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(answer)
            # add llm's response to conversation history
            st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
