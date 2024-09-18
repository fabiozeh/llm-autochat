# Autochat: a tool for automating LLM tests.

Autochat is a CLI tool for simplifying the task of collecting multiple responses from a chatbot.

## Installation

Clone the repository. That's about it.

The repository includes a bash script to create, activate and populate a Python virtual environment for the sake of running the tool. If you choose to use it, simply add execution permissions to `autochat` and use that script to invoke the tool. If not, install the dependencies from the `requirements.txt` file (`pip install -r requirements.txt` should suffice) and use the python script `autochat.py` directly.

## Usage

Create a text file containing the prompts to send sequentially to the LLM. Each message must be separated from the previous one by two blank lines. The `sample_inputs` directory contains examples. Assuming a local Ollama installation in the standard port:

```bash
./autochat --url http://localhost:11434/api/chat --model mistral sample_inputs/three_questions.txt
```

Or, using the Python script directly:

```bash
python autochat.py --url http://localhost:11434/api/chat --model mistral sample_inputs/three_questions.txt
```

To simplify usage, you may also set the URL in an environment variable `LLM_API_URL` instead.

## Other Features

- Custom API parameters via the `--raw` option
- Independent messages or conversations with history

See the help for details.

```bash
./autochat --help
```

