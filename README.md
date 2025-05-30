# Natural language processing course 2024/2025: `Conversational Agent with Retrieval-Augmented Generation`

The project will involve natural language processing (NLP), web scraping, and retrieval-augmented generation (RAG) techniques to provide quality answers for news in real time.

## Environment Setup

You can set up the required environment using either `pip` with `requirements.txt` or `conda` with `environment.yml`. Choose **one** method.

### Option 1: Using `pip` (Recommended for Python-only dependencies)

1.  **(Optional but Recommended)** Create and activate a virtual environment:

    ```bash
    python -m venv venv
    # On Windows:
    # venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

2.  Install the requirements:
    ```bash
    pip install -r requirements.txt
    ```

### Option 2: Using `conda` (Recommended for complex dependencies or full environment replication)

_Ensure you have Conda or Miniconda installed._

1.  Create the environment from the `environment.yml` file:

    ```bash
    conda env create -f environment.yml
    ```

    _(This might take a few minutes)_

2.  Activate the newly created environment (the environment name is usually defined inside the `.yml` file, check it if unsure):
    ```bash
    conda activate <your_environment_name>
    ```

You should now have the necessary dependencies installed to run the project.

## Additional Setup Steps

After setting up your environment using either `pip` or `conda` and installing the requirements, you need to download the Slovene language model for spaCy. Run the following command in your terminal (ensure your virtual environment is activated if you are using one):

```bash
python -m spacy download sl_core_news_sm
```

This model is necessary for natural language processing tasks in Slovene within the project.

## Configuration

1.  **Environment Variables:**
    Create a `.env` file inside the `src/` directory (`src/.env`).
    This file is used to store sensitive information and configuration settings.

2.  **Required Variables:**
    Add the following variables to your `src/.env` file:

    ```dotenv
    # Necessary for connecting to the PostgreSQL database (adjust if needed - see src/docker-compose-yaml)
    DATABASE_URL=postgresql://test:test@localhost:5432/test

    # Optional: Add your OpenAI API key to use the OpenAI LLM provider
    # If omitted, and GEMINI_API_KEY is also omitted, the application will use the local (mocked) provider.
    # OPENAI_API_KEY=sk-...

    # Optional: Add your Gemini API key to use the Gemini LLM provider
    # If omitted, and OPENAI_API_KEY is also omitted, the application will use the local (mocked) provider.
    # GEMINI_API_KEY=AIza...
    ```

## Running the Application

1.  **Navigate to the Source Directory:**
    Open your terminal and change to the `src/` directory:

    ```bash
    cd src
    ```

2.  **Start Services with Docker Compose:**
    Ensure Docker is running. Then, start the database service defined in `docker-compose.yml`:

    ```bash
    docker compose up -d # The -d flag runs it in detached mode (background)
    ```

    Wait a few moments for the database container to initialize.

3.  **Run the Main Script:**
    Execute the main Python script to start the chatbot:

    ```bash
    python main.py
    ```

    Optional flags:

    - `--use-chat-history`: Enable conversation history.

4.  **Stopping Services:**
    When you are finished, stop the Docker Compose services:
    ```bash
    docker compose down
    ```

## Authors

| **Blaž Špacapan**                                                                                                                                                  | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Matevž Jecl**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;                                                                                      | **Tilen Ožbot**                                                                                                                                          |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| <p align="center">[<img src="https://github.com/blazspacaS.png" alt="Blaž Špacapan" width="80px" style="border-radius: 50%;"/>](https://github.com/blazspacaS)<p/> | <p align="center">[<img src="https://github.com/matevzjecl.png" alt="Matevž Jecl" width="80px" style="border-radius: 50%;"/>](https://github.com/matevzjecl)<p/> | <p align="center">[<img src="https://github.com/tilenn.png" alt="Tilen Ožbot" width="80px" style="border-radius: 50%;"/>](https://github.com/tilenn)<p/> |
