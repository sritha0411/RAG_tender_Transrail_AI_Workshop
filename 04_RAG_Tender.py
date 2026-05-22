import streamlit as st
import time
import os
import sys

st.title("📚 Task 4: The 1,000-Page Tender Interrogator")

st.markdown("""
**The Context:** Bidding for PGCIL or international EPC tenders involves digesting hundreds of pages of complex legal and technical constraints.
We will build a Retrieval-Augmented Generation (RAG) pipeline to ground an LLM in a specific document.
""")

st.write("### 🗄️ Vector Database Context")
st.info("For this workshop, we assume a dummy 50-page PDF tender document has already been chunked and loaded into ChromaDB.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "I have ingested the 'PGCIL 400kV Substation Tender v2.pdf'. What would you like to know?"}
    ]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 🛑 PARTICIPANT CODE GOES HERE 🛑
# ==========================================
def run_rag_pipeline(user_query):
    """
    TODO: Implement the RAG logic.
    1. Embed the user query.
    2. Search the vector database (ChromaDB) for the top 3 similar chunks.
    3. Pass the chunks + query to the LLM to generate an answer.
    4. Ensure it returns a citation!
    """
    # --- WRITE YOUR RAG PIPELINE HERE ---

    try:
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
        from langchain_community.vectorstores import Chroma
        from langchain_core.prompts import PromptTemplate
        from langchain.chains import RetrievalQA
        
        # 1. Embed the query and connect to ChromaDB
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
        
        # 2. Search vector DB for top 3 chunks
        docs = vectorstore.similarity_search(user_query, k=3)
        
        # Debug: Show retrieved chunks in an expander
        with st.expander("🔍 Internal AI Research (Retrieved Chunks)"):
            for i, doc in enumerate(docs):
                st.markdown(f"**Chunk {i+1} (Page {doc.metadata.get('page')})**")
                st.text(doc.page_content)
        
        # 3. Choose LLM model
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        
        # 4. Manually build context string with metadata
        context_parts = []
        for doc in docs:
            p = doc.metadata.get('page', 'Unknown')
            context_parts.append(f"[Content from Page {p}]: {doc.page_content}")
        context_string = "\n\n".join(context_parts)

        # HCI Challenge: Custom prompt forcing citation
        prompt_template = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer, based ONLY on the context below, just say that you don't know. 
Do not use outside knowledge. Do not hallucinate.

Context: {context}

Question: {question}

Important: Always include a plain text citation in the format [Source: pg. X] where X is the page number you found in the context. Do NOT use clickable Markdown links.
Answer:"""
        
        final_prompt = prompt_template.format(context=context_string, question=user_query)
        
        # 5. Generate Answer
        response = llm.predict(final_prompt)
        return response
        
    except Exception as e:
        return f"⚠️ RAG Pipeline Error: {str(e)}"
    # ------------------------------------

# ==========================================

# React to user input
if prompt := st.chat_input("Ask a question about the tender..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching document vectors..."):
            response = run_rag_pipeline(prompt)
            st.markdown(response)
            
            st.success("💡 **HCI Challenge:** Notice the 'Source' citation. Can you see how grounding provides verifiable answers?")
            
    st.session_state.messages.append({"role": "assistant", "content": response})
