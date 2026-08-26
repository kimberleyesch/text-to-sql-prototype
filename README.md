# Text-to-SQL Prototype
This prototype was developed to test whether retrieval-augmented generation (RAG) improves the executability and accuracy of a Text-to-SQL system.
It uses a large language model to generate SQL queries from natural-language business questions.
Its executability is evaluated automatically by executing the generated query against the test database.
Its accuracy is evaluated manually by comparing the generated query results with the expected results.

During a test run, the program:
- reads the database schema from an SQLite database
- reads a predefined set of test questions
- creates a prompt for each question
- generates SQL queries using an LLM
- executes the generated queries
- saves each generated query and result into a CSV file

## Requirements
- Python 3.13
- Google Gemini API key

Create a `.env` file in the project root and add the API key:
```GEMINI_API_KEY=your_api_key```

## Installation
Clone this repository and install the required dependencies:
```py -m pip install -r requirements.txt```

## Project Structure
- `database_setup/`: Creates and fills the SQLite database
- `evaluation/`: Saves and evaluates the test results
- `evaluation/results/`: Contains test results
- `rag/`: Contains RAG pipeline script
- `rag/documents/`: Contains documents used for retrieval
- `src/`: Contains prototype implementation
- `main.py`: Runs the complete test process

## Test Database
The test database is a synthetic relational business database containing customers, products, categories, orders, and order_items.
To create the test database, navigate to the database_setup directory and execute create_sql_database.py

## Run
- Install dependencies
- Add Gemini API key
- Create the SQLite test database
- Set desired configuration in main.py
- For the first RAG run, set `REBUILD_RAG_COLLECTION = True` to create local ChromaDB collection
- Run ```py main.py```

The execution mode is controlled by the configuration variables described below.

## Configuration
The following configuration variables are found in main.py:

`USE_RAG`
- False: Generates SQL queries without retrieval context.
- True: Retrieved context is provided to the LLM.

`REBUILD_RAG_COLLECTION`
- False: Uses the existing local vector collection.
         The ChromaDB collection is generated locally and is not included in
         the repository. Before using RAG for the first time, set this to True.
- True: Recreates the vector collection from the RAG documents

## Large Language Model
The large language model used in this prototype is Gemini 3.5 Flash.
It receives a prompt for each question containing the user's question, the database schema,
and instructions requiring the model to generate only SELECT statements.
When RAG is activated, the three most relevant documents are additionally added to the prompt.

## Retrieval-Augmented Generation
The embeddings are generated using Gemini Embedding 2 and stored in a local ChromaDB collection.
For each test question, the three most relevant documents are retrieved using cosine similarity and added to the LLM prompt.

## Results
The results are saved in `evaluation/results/`.
The results folder is created automatically if it does not exist.
For each test run, a separate folder is created in `evaluation/results/`. It contains files with the generated SQL queries and their corresponding results, as well as additional evaluation information, such as executability results, and LLM-generated thinking summaries.
When RAG is activated, the document distances for all available RAG documents are also stored in the directory.