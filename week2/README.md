# Action Item Extractor

A FastAPI + SQLite web application that converts free-form notes into structured, actionable checklist items. Supports both heuristic-based and LLM-powered extraction.

## Project Structure

```
week2/
├── app/
│   ├── main.py              # FastAPI entry point with lifespan management
│   ├── db.py                # SQLite database access layer
│   ├── schemas.py           # Pydantic request/response models
│   ├── routers/
│   │   ├── notes.py         # Notes CRUD endpoints
│   │   └── action_items.py  # Action item extraction & management endpoints
│   └── services/
│       └── extract.py       # Heuristic + LLM extraction logic
├── frontend/
│   └── index.html           # Single-page HTML frontend
├── tests/
│   └── test_extract.py      # Unit tests for extraction functions
└── data/
    └── app.db               # SQLite database (auto-created at runtime)
```

## Setup & Run

### Prerequisites

- Python 3.10+
- [Conda](https://docs.conda.io/) with the `cs146s` environment
- [Ollama](https://ollama.com/) installed and running (for LLM extraction)

### Install & Start

1. Activate the conda environment:
   ```bash
   conda activate cs146s
   ```

2. Pull an Ollama model (first time only):
   ```bash
   ollama run llama3.2
   ```

3. Start the server from the project root:
   ```bash
   poetry run uvicorn week2.app.main:app --reload
   ```

4. Open http://127.0.0.1:8000/ in your browser.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `llama3.2` | Ollama model name for LLM extraction |

## API Endpoints

### Notes

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/notes` | Create a new note (`{"content": "..."}`) |
| `GET`  | `/notes` | List all saved notes |
| `GET`  | `/notes/{note_id}` | Retrieve a single note by ID |

### Action Items

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/action-items/extract` | Extract action items using heuristic rules |
| `POST` | `/action-items/extract-llm` | Extract action items using Ollama LLM |
| `GET`  | `/action-items` | List all action items (optional `?note_id=` filter) |
| `POST` | `/action-items/{id}/done` | Toggle done status (`{"done": true/false}`) |

Both extract endpoints accept:
```json
{
  "text": "your notes here...",
  "save_note": true
}
```

## Running Tests

From the project root:

```bash
poetry run pytest week2/tests/ -v
```

The test suite covers:
- Heuristic extraction (bullets, checkboxes, numbered lists)
- LLM extraction (mocked Ollama calls for bullet lists, keyword-prefixed lines, free-form paragraphs, empty input, error handling)
