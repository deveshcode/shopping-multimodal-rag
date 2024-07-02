# Nike Product Search Bot

Welcome to the Nike Product Search Bot! This application helps you search for Nike products using both text queries and image uploads. Built with Streamlit, it leverages the CLIP model for embeddings and Pinecone for vector database management. Below you'll find instructions on how to run and use the app.

<img width="1276" alt="Screenshot 2024-07-01 at 10 01 33 PM" src="https://github.com/deveshcode/shopping-multimodal-rag/assets/37287532/6de1a49e-242e-4836-bcf8-dca0e9346eba">

It performs search functionality as follows : 

<img width="1280" alt="Screenshot 2024-07-01 at 10 05 28 PM" src="https://github.com/deveshcode/shopping-multimodal-rag/assets/37287532/ce713ad3-4df3-4067-8004-5019404546c2">

Further now, you can also virtually try it on by providing your image and product image :

<img width="1280" alt="Screenshot 2024-07-02 at 7 22 59 PM" src="https://github.com/deveshcode/shopping-multimodal-rag/assets/37287532/97c1d403-7dee-4bee-9f39-0ede08e56b55">

## Installation

Instructions on how to install and set up your project. Include any necessary commands.

```bash
git clone https://github.com/deveshcode/shopping-multimodal-rag.git
cd shopping-multimodal-rag
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the root directory and add your Pinecone API key:

```env
PINECONE_API_KEY=your_pinecone_api_key
OPENAI_API_KEY=your_open_ai_key
API_HOST=http://localhost:8001
BUCKET_NAME=gcs_bucket_name 
GOOGLE_APPLICATION_CREDENTIALS=gcloud_creds_json_file
azure_cv_key=azure_cv_key
azure_cv_endpoint=azure_cv_endpoint
```

## Usage

To run the REST API server, we need to run the FAST API by executing the following command:

```bash
uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

Next, to run the streamlit app, we need to run the FAST API by executing the following command:

```bash
streamlit run app.py
```
Open the provided URL in your web browser to access the application.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

## License

Distributed under the MIT License. See `LICENSE` for more information.
