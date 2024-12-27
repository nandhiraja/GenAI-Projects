# Legal Document Summarization

This project focuses on building an AI-driven system for summarizing legal documents and enabling question-answering based on the content.

## Features
- **Legal Document Summarization**: Splits documents into manageable chunks for processing.
- **Embeddings**: Uses HuggingFace Embeddings to represent text.
- **Retrieval-Based QA**: Powered by Llama 3.2 model through Groq API.

## Requirements
- Install the required libraries using `requirements.txt`.
- Provide your `GROQ_API_KEY` in a `.env` file.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/legal-doc-summarization.git
   cd legal-doc-summarization
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file and add your `GROQ_API_KEY`:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

## Usage
Run the script:
```bash
python main.py
```

Provide the file path for your legal document when prompted.

## Example
After running the script, input a file path:
```
: Enter the file path :_ /path/to/legal_document.txt
```

Then, ask your questions:
```
--: Ask the Question : What are the key clauses in the agreement?
```

## Contributions
Feel free to fork and submit pull requests!


