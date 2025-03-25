import ollama
import streamlit as st
from openai import OpenAI

# Set the streamlit page config
st.set_page_config(page_title="SRS Generator", page_icon="-", layout="wide")


# get the models from the ollama API
def get_models(models_info: list) -> tuple:
    return tuple(model["model"] for model in models_info["models"])

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

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with message_container.chat_message(message["role"]):
            st.markdown(message["content"])
            
    uploaded_files = st.sidebar.file_uploader(
            label="Upload", type=["txt"], accept_multiple_files=True
        )
    
    raw_text=""
    for file in uploaded_files:
        raw_text += str(file.read(),"utf-8") + "\n"

    if prompt := st.chat_input("Enter your message"):
        try:
            st.session_state.messages.append({"role": "user", "content": prompt + raw_text})
            raw_text = ""
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
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

# # Initialize the prompt
# system_prompt_file = open("data/system_prompt.txt", "r",encoding="utf8")
# system_prompt = system_prompt_file.read()
# system_prompt_file.close()

# # Initial prompt for the model which will be prepended to the user input
# initial_prompt_file = open("data/prompt.txt", "r",encoding="utf8")
# initial_prompt = initial_prompt_file.read()
# initial_prompt_file.close()
