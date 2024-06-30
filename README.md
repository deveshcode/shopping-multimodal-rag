# Nike Product Search Bot

Welcome to the Nike Product Search Bot! This application helps you search for Nike products using both text queries and image uploads. Built with Streamlit, it leverages the CLIP model for embeddings and Pinecone for vector database management. Below you'll find instructions on how to run and use the app.

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
```

## Usage

To run the app, execute the following command:

```bash
streamlit run app.py
```
Open the provided URL in your web browser to access the application.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

## License

Distributed under the MIT License. See `LICENSE` for more information.
