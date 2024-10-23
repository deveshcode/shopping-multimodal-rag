Github Repo for StyleScout Multimodal RAG

## Video Demo

[![Video Demo](https://img.shields.io/badge/Video%20Demo-<COLOR>?style=for-the-badge&logo=<LOGO>&logoColor=white)](https://youtu.be/ZygyXm84pUQ)

## Documentation

[![codelabs](https://img.shields.io/badge/codelabs-4285F4?style=for-the-badge&logo=codelabs&logoColor=white)](https://codelabs-preview.appspot.com/?file_id=16XmZAjcqcY8qKhQ87nAlNkNS5XIRCKnQzeiKVg-XPUE#0)

# StyleScout - LLM-Powered Personal Stylist

Welcome to the StyleScout! This application helps you search for Fashion products using both text queries and image uploads. Built with Streamlit, it leverages the CLIP model for embeddings and Pinecone for vector database management.

![Screenshot 2024-10-12 at 1 28 54 PM](https://github.com/user-attachments/assets/c0b8f6a0-cb87-40a7-97a3-dbed4c3333de)

![2](https://github.com/user-attachments/assets/fba9b953-d7bd-450a-95e0-b69d1d6babd0)

![3](https://github.com/user-attachments/assets/ee9c5a1d-b5a6-4b65-8be9-a266806d3f52)

![4](https://github.com/user-attachments/assets/d3a72a4b-4196-4bea-8c6e-6eb9068aefee)

![5](https://github.com/user-attachments/assets/9e78ec28-cb00-4a8f-9c1e-2d0158d8a4bc)

## Features


### Product Search

It performs search functionality as follows:

![Screenshot 2024-10-12 at 1 32 09 PM](https://github.com/user-attachments/assets/4e64889c-e796-4cbe-b37a-29f3bd1e2902)

![6](https://github.com/user-attachments/assets/b9e5adb0-b474-45cf-955b-965a0c12b46a)

![7](https://github.com/user-attachments/assets/d079e310-4a3c-4835-adff-c345fb138acb)

![8](https://github.com/user-attachments/assets/b3fd9586-9cdc-42ec-9350-87b601d902a5)


### Virtual Try-On
You can also virtually try it on by providing your image and product image:

<img width="1280" alt="redtrackvirtualtryon" src="https://github.com/user-attachments/assets/eed1e735-05be-4945-ae37-df152fce16fc">


## Installation

1. Git clone the repository:

```bash
git clone https://github.com/deveshcode/shopping-multimodal-rag.git
cd shopping-multimodal-rag
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Create a .env file in the root directory and add your API keys:

```bash
PINECONE_API_KEY=your_pinecone_api_key
OPENAI_API_KEY=your_open_ai_key
API_HOST=http://localhost:8001
BUCKET_NAME=gcs_bucket_name 
GOOGLE_APPLICATION_CREDENTIALS=gcloud_creds_json_file
azure_cv_key=azure_cv_key
azure_cv_endpoint=azure_cv_endpoint
```

## Data Scraping and Embedding Pipeline

To collect data and create embeddings for the Fashion Product Search Bot, you can follow the steps below:

1. Run the `01_scrapper.py` script to scrape data from the Fashion website and save it as a CSV file.

2. Upload the CSV file to an S3 bucket using the `02_upload_to_s3.py` script. Make sure you have the necessary AWS credentials configured.

3. Use the `03_pinecone_storing_data.py` script to create a Pinecone index and upload the embeddings to Pinecone. This will allow you to perform efficient similarity searches on the data.

By following this pipeline, you can ensure that the Fashion Product Search Bot has up-to-date data and accurate embeddings for product search and virtual try-on functionalities.

Remember to customize the scripts according to your specific requirements and configurations.

## Usage

To run the REST API server:

```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

To run the Streamlit app:

```bash
cd frontend
streamlit run app.py
```

Open the provided URL in your web browser to access the application.

## Tools and Technologies

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![CLIP](https://img.shields.io/badge/CLIP-FF4B4B?style=for-the-badge&logo=openai&logoColor=white)](https://beta.openai.com/docs/)
[![Pinecone](https://img.shields.io/badge/Pinecone-FF4B4B?style=for-the-badge&logo=pinecone&logoColor=white)](https://www.pinecone.io/docs/)
[![Google Cloud Storage](https://img.shields.io/badge/Google%20Cloud%20Storage-FF4B4B?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/storage/docs)
[![Azure Cognitive Services](https://img.shields.io/badge/Azure%20Cognitive%20Services-FF4B4B?style=for-the-badge&logo=microsoft-azure&logoColor=white)](https://docs.microsoft.com/en-us/azure/cognitive-services/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/)

## Data Sources
Data collected from the following sources:
Nike Website : https://www.nike.com/

## Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

## License
Distributed under the MIT License. See LICENSE for more information.

## References
1. OpenAI API Documentation: https://beta.openai.com/docs/ 
2. Pinecone Documentation: https://www.pinecone.io/docs/ 
3. FastAPI Documentation: https://fastapi.tiangolo.com/ 
4. Streamlit Documentation: https://docs.streamlit.io/ 
5. Google Cloud Storage Documentation: https://cloud.google.com/storage/docs 
6. Azure Cognitive Services Documentation: https://docs.microsoft.com/en-us/azure/cognitive-services/ 
