# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **Jiaxiang** \
SUNet ID: **jiaxiang** \
Citations: Ollama Structured Outputs https://ollama.com/blog/structured-outputs ; FastAPI docs https://fastapi.tiangolo.com/ ; Pydantic V2 docs https://docs.pydantic.dev/

This assignment took me about **3** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: 
```
Analyze the existing extract_action_items() function in week2/app/services/extract.py.
Implement an LLM-powered alternative extract_action_items_llm() that uses Ollama to
extract action items via a large language model. Use a Pydantic model with Ollama's
format parameter for structured JSON output. Model name configurable via OLLAMA_MODEL
env var (default llama3.2). Return empty list for empty input, raise RuntimeError on failure.
``` 

Generated Code Snippets:
```
week2/app/services/extract.py (lines 9, 93-129):
  - Line 9: Added from pydantic import BaseModel
  - Line 93: OLLAMA_MODEL env var config
  - Lines 96-97: ActionItems Pydantic model for structured output schema
  - Lines 100-128: extract_action_items_llm() using Ollama chat API with
    format=ActionItems.model_json_schema() and Pydantic validation
```

### Exercise 2: Add Unit Tests
Prompt: 
```
Write unit tests for extract_action_items_llm() in week2/tests/test_extract.py.
Use unittest.mock.patch to mock Ollama chat calls. Cover: bullet lists, keyword-prefixed
lines (todo:/action:), empty input, whitespace-only input, text with no action items,
free-form paragraphs, and Ollama connection errors.
``` 

Generated Code Snippets:
```
week2/tests/test_extract.py (full file, lines 1-119):
  - Lines 1-5: Imports (pytest, unittest.mock, extraction functions)
  - Lines 10-22: Original test_extract_bullets_and_checkboxes (preserved)
  - Lines 27-32: _mock_chat_response() helper
  - Lines 35-53: test_llm_extract_bullet_list
  - Lines 56-70: test_llm_extract_keyword_prefixed
  - Lines 73-77: test_llm_extract_empty_input
  - Lines 80-84: test_llm_extract_whitespace_only
  - Lines 87-93: test_llm_extract_no_action_items
  - Lines 96-111: test_llm_extract_freeform_paragraph
  - Lines 113-118: test_llm_extract_raises_on_ollama_error
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
```
Refactor the week2 backend code focusing on:
1. API contracts/schemas: Create Pydantic models replacing all Dict[str, Any] in routers
2. Database layer cleanup: Simplify db.py with executescript, enable PRAGMA foreign_keys
3. App lifecycle/configuration: Replace module-level init_db() with FastAPI lifespan context manager
4. Error handling: Add proper exception handling and HTTP error responses in routers
``` 

Generated/Modified Code Snippets:
```
week2/app/schemas.py (new file, lines 1-54):
  - NoteCreateRequest, NoteResponse, ExtractRequest, ActionItemResponse,
    ExtractResponse, ActionItemDetail, MarkDoneRequest, MarkDoneResponse

week2/app/main.py (rewritten, lines 1-35):
  - Lines 18-21: asynccontextmanager lifespan for init_db()
  - Line 24: FastAPI with lifespan parameter
  - Line 15: FRONTEND_DIR extracted as module constant

week2/app/db.py (refactored, lines 1-99):
  - Line 24: PRAGMA foreign_keys = ON
  - Lines 30-48: executescript for table creation
  - Lines 53-99: Simplified CRUD functions using conn.execute

week2/app/routers/notes.py (refactored, lines 1-39):
  - Pydantic schemas replace Dict[str, Any]
  - Added list_all_notes() endpoint (GET /notes)

week2/app/routers/action_items.py (refactored, lines 1-74):
  - All endpoints use Pydantic request/response models
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```
Using Cursor Agent mode:
1. Integrate LLM extraction as POST /action-items/extract-llm endpoint, reuse
   ExtractRequest/ExtractResponse schemas, return HTTP 502 on Ollama failure.
2. Expose GET /notes to list all notes.
3. Update frontend: add "Extract LLM" button calling /action-items/extract-llm,
   add "List Notes" button calling GET /notes, extract common doExtract() function.
``` 

Generated Code Snippets:
```
week2/app/routers/action_items.py (lines 37-52):
  - extract_llm() endpoint — POST /action-items/extract-llm

week2/app/routers/notes.py (lines 24-30):
  - list_all_notes() endpoint — GET /notes

week2/frontend/index.html (lines 1-114):
  - Line 31: "Extract LLM" button
  - Line 32: "List Notes" button
  - Lines 37-40: Notes display section
  - Lines 46-82: doExtract(endpoint) shared function
  - Lines 87-110: List Notes click handler with note card rendering
```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
Analyze the week2 codebase and generate a well-structured README.md including:
project overview, directory structure, prerequisites and setup instructions
(conda, Ollama, Poetry), environment variables, all API endpoints in table format,
and test suite instructions.
``` 

Generated Code Snippets:
```
week2/README.md (new file):
  - Project overview: FastAPI + SQLite action item extractor
  - Directory structure tree
  - Setup & Run: conda env, Ollama model pull, uvicorn start
  - Environment variables table (OLLAMA_MODEL)
  - API endpoints tables: Notes (3) + Action Items (4)
  - Test instructions: poetry run pytest command and coverage summary
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 
