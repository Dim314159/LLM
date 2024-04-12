# Quiz creator
In order to use this you need to create project in Google cloud and download the .json key.

Go to file quiz.py and put correct credentials
if __name__ == "__main__":
    embed_config = {
        "model_name": "textembedding-gecko@003",
        # use your project id
        "project": "Your Project ID",
        "location": "us-central1"
    }

in terminal:
streamlit run .\quiz.py
