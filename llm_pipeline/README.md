# OpenAlex Scraping + LLM Pipeline

This project automates the retrieval of project info (e.g. funding grants) of academic papers from OpenAlex using LLMs.

## Workflow

1.  **Fetch Metadata**: Retrieves paper metadata from OpenAlex filtered by specific criteria.
2.  **Download PDFs**: Downloads the (open-access) PDFs for the retrieved papers.
3.  **Convert to Markdown**: Converts PDF content into Markdown format for processing.
4.  **AI Extraction**: Uses an AI agent (Pydantic AI) to extract structured data (publications, grants) from the text.
5.  **Output**: Generates JSON files with the extracted information.

## Usage

This project uses OpenRouter as the API gateway for LLM providers, and the Pydantic AI Python framework for building the agent.

You first must set the OpenRouter API key by creating a `.env` file as such:
```text
OPENROUTER_API_KEY=sk-...
```

You can get an OpenRouter API key here: https://openrouter.ai.


Open and run the cells in `main_agent.ipynb` to execute the pipeline steps sequentially.