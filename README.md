# srs-with-llm
This repository contains work for my masters thesis - "Using LLMs for Requirements Engineering"

# Install and create a virtual environment and activate it to install the packages in the requirements document.
- [Instructions on setting up Virtualenv](https://docs.python.org/3/library/venv.html)

# Install the requirements
`pip install -r requirements.txt`

# Create file ".streamlit/secrets.toml" and add the below properties in KEY=VALUE format replacing "value" with actual value
`API_URL=value`
`API_KEY=value`

# Run the application using below command
`streamlit run script.py`