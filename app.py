import streamlit as st
from streamlit_folium import st_folium
import os
from pathlib import Path
from crawl import crawl_local_repo  # This function will be defined to crawl local repo
from db import *
from llm import *
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

openai_api_key = os.getenv("OPENAI_API_KEY")
persist_directory = os.getenv("CHROMA_DIR")


def main():
    st.title("RepoGPT")
    default_api_key = os.getenv("OPENAI_API_KEY")
    openai_api_key = st.sidebar.text_input(
        "OpenAI API Key", type="password", value=default_api_key
    )

    gpt_model = st.sidebar.radio(
        "Select GPT model:",
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

    # example_path = "/Users/wei/Misc/Media-Transport-Library"
    example_path = "/Users/wei/Misc/RepoGPT-for-test"

    repo_path = st.sidebar.text_input(
        "Enter local repository path",
        value=example_path,
    )

    if not repo_path or not os.path.isdir(repo_path):
        st.sidebar.warning("Please enter a valid local repository path.")
        return

    file_rel_paths = crawl_local_repo(repo_path, rel_path=True)

    if "show_files" not in st.session_state:
        st.session_state["show_files"] = False
    if st.sidebar.button(f"Show or Hide {len(file_rel_paths)} files"):
        st.session_state["show_files"] = not st.session_state["show_files"]
    if st.session_state["show_files"]:
        for file_path in file_rel_paths:
            st.sidebar.write(file_path)

    if st.sidebar.button("Select existing chroma persist db"):
        persist_path = st.sidebar.text_input(
            "Enter chroma persist path",
            value="",
        )
        st.sidebar.write("/Users/wei/Misc/RepoGPT-for-test/_chroma3")
        vectordb = load_vector_db(openai_api_key, persist_path)
        if vectordb is not None:
            st.sidebar.write("Loaded vectordb complete.")
            st.session_state["vectordb"] = vectordb
        else:
            st.sidebar.error("Failed to load vectordb.")

    chroma_dir_name = st.sidebar.text_input(
        "Enter the name of persist directory", value="chroma3"
    )
    # chroma_dir_name = os.path.basename(repo_path) + "_" + chroma_dir_name
    # persist_directory = os.path.join(os.path.dirname(repo_path), chroma_dir_name)

    if st.sidebar.button("Create new chroma persist db"):
        persist_directory = os.path.join(repo_path, "_" + chroma_dir_name)

        if os.path.exists(persist_directory):
            st.sidebar.warning(
                "Persist directory already exists. Are you sure you want to overwrite it?"
            )
            # return
            # if not st.sidebar.button("Overwrite it."):  # this is not working for now
            #     return

        st.sidebar.write(f"Vectorizing the documents in {persist_directory}...")
        vectordb = get_vectordb(openai_api_key, repo_path, persist_directory)
        st.sidebar.write("Vectorization complete.")
        st.session_state["vectordb"] = vectordb

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Chat with RepoGPT"):
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
