# Text-to-SQL Prototype

This prototype uses a large language model to generate SQL queries from
natural-language business questions.
Its accuracy is evaluated by comparing the results generated with and without retrieval-augmented generation (RAG).

During a test run, the program:
- reads the database schema from an SQLite database
- reads a set of 50 test questions
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
Clone this repository and install the requirement dependencies:
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
To create the test database navigate to database_setup and execute create_sql_database.py

## Run
Run the prototype from the project root:
```py main.py```

The execution mode is controlled by the configuration variables described below.

## Configuration
The following configurations are found in main.py:

- `USE_RAG = False`: Generates SQL queries without retrieval context.
- `USE_RAG = True`: Retrieval generated context is provided to the LLM.
- `REBUILD_RAG_COLLECTION = False`: Uses the existing local vector collection.
                                    The ChromaDB collection is generated locally and is not included in
                                    the repository. Before using RAG for the first time, set this to True.
- `REBUILD_RAG_COLLECTION = True`: Recreates the vector collection from the RAG documents

## Large Language Model
The large language model used in this prototype is Gemini 3.5 Flash.
It receives a prompt for each question containing the user's question, the database schema,
and instructions such as only SELECT queries are allowed to be executed.

## Retrieval-Augmented Generation
The embeddings are generated and retrieved by Gemini Embedding 2.
They are stored in a ChromaDB collection.
The most relevant documents are retrieved for each question and added to the LLM prompt.

## Results
The results are saved in `evaluation/results/`.
The results folder is created automatically if it doesn't exist.
Depending on whether RAG is activated or not, the files are saved in `evaluation/results/without_rag` or `evaluation/results/with_rag`.
Each file is named by the question ID and contains the generated SQL query and query result.
If RAG is set to True the file name will be appended with "_RAG".

## Evaluation
#TODO