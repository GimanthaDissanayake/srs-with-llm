import uuid
import re
import ollama
import streamlit as st
from openai import OpenAI
from markdown import markdown
from xhtml2pdf import pisa

# Set the streamlit page config
st.set_page_config(page_title="SRS Generator", page_icon="-", layout="wide")

# Initialize the system prompt
def initialize_system_prompt():
    system_prompt_file = open("data/system_prompt.txt", "r",encoding="utf8")
    system_prompt = system_prompt_file.read()
    system_prompt_file.close()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": system_prompt}
        ]

# get the models from the ollama API
def get_models(models_info: list) -> tuple:
    return tuple(model["model"] for model in models_info["models"])

# remove <think> tags from the text
def remove_think_tags(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

# create a PDF file from the text
def create_pdf(text, filename="response.pdf"):
    html = markdown(text)  # Convert Markdown to HTML
    with open(filename, "w+b") as f:
        pisa.CreatePDF(html, dest=f)
    return filename

# create the download button for the PDF file
def create_download_button(response):
    last_response = remove_think_tags(response)
    pdf_file = create_pdf(last_response)

    with open(pdf_file, "rb") as f:
        st.download_button(
            "Download as PDF (Markdown)",
            key = f"download_{uuid.uuid4()}",
            data=f,
            file_name="ai_response.pdf",
            mime="application/pdf",
        )

# handle user input and process the response
def handle_user_input(client, message_container, prompt, selected_model):
    st.session_state.messages.append({"role": "user", "content": prompt})
    message_container.chat_message("user").markdown(prompt)

    with message_container.chat_message("assistant"):
        with st.spinner("Processing..."):
            stream = client.chat.completions.create(
                        model=selected_model, 
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ], 
                        stream=True
                    )
        
        response = st.write_stream(stream)

        create_download_button(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

def main():
    client = OpenAI(base_url=st.secrets["API_URL"],
                    api_key=st.secrets["API_KEY"])

    models_info = ollama.list()
    available_models = get_models(models_info)

    if available_models:
        selected_model = st.selectbox("Select a model", available_models)
    else:
        st.error("No models available. Please try again after pulling a model from Ollama.")

    message_container = st.container(height=500, border=True)

    # Initialize chat history with system prompt ONLY ONCE
    initialize_system_prompt()

    # Display all messages except system prompt (hidden from UI)
    for message in st.session_state.messages:
        if message["role"] != "system":  # Skip showing system prompt in UI
            with message_container.chat_message(message["role"]):
                st.markdown(message["content"])  
     
    if prompt := st.chat_input("Enter your message"):
        try:
            handle_user_input(client, message_container, prompt, selected_model)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
