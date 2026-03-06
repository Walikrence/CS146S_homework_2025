import os
import pytest
from unittest.mock import patch, MagicMock

from ..app.services.extract import extract_action_items, extract_action_items_llm


# --------------- Tests for heuristic extract_action_items ---------------

def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


# --------------- Tests for LLM-powered extract_action_items_llm ---------------

def _mock_chat_response(items: list[str]) -> MagicMock:
    """Build a mock Ollama chat response containing the given items."""
    import json
    response = MagicMock()
    response.message.content = json.dumps({"items": items})
    return response


@patch("week2.app.services.extract.chat")
def test_llm_extract_bullet_list(mock_chat):
    mock_chat.return_value = _mock_chat_response([
        "Set up database",
        "Implement API endpoint",
        "Write tests",
    ])

    text = """
    - Set up database
    - Implement API endpoint
    - Write tests
    """
    result = extract_action_items_llm(text)
    assert len(result) == 3
    assert "Set up database" in result
    assert "Implement API endpoint" in result
    assert "Write tests" in result
    mock_chat.assert_called_once()


@patch("week2.app.services.extract.chat")
def test_llm_extract_keyword_prefixed(mock_chat):
    mock_chat.return_value = _mock_chat_response([
        "Fix login bug",
        "Update documentation",
    ])

    text = """
    todo: Fix login bug
    action: Update documentation
    """
    result = extract_action_items_llm(text)
    assert len(result) == 2
    assert "Fix login bug" in result
    assert "Update documentation" in result


@patch("week2.app.services.extract.chat")
def test_llm_extract_empty_input(mock_chat):
    result = extract_action_items_llm("")
    assert result == []
    mock_chat.assert_not_called()


@patch("week2.app.services.extract.chat")
def test_llm_extract_whitespace_only(mock_chat):
    result = extract_action_items_llm("   \n\t  ")
    assert result == []
    mock_chat.assert_not_called()


@patch("week2.app.services.extract.chat")
def test_llm_extract_no_action_items(mock_chat):
    mock_chat.return_value = _mock_chat_response([])

    text = "The weather is nice today."
    result = extract_action_items_llm(text)
    assert result == []


@patch("week2.app.services.extract.chat")
def test_llm_extract_freeform_paragraph(mock_chat):
    mock_chat.return_value = _mock_chat_response([
        "Schedule follow-up meeting",
        "Send project proposal",
    ])

    text = (
        "We had a great meeting today. We need to schedule a follow-up meeting "
        "next week. Also, please send the project proposal to the client by Friday."
    )
    result = extract_action_items_llm(text)
    assert len(result) == 2
    assert "Schedule follow-up meeting" in result
    assert "Send project proposal" in result


@patch("week2.app.services.extract.chat")
def test_llm_extract_raises_on_ollama_error(mock_chat):
    mock_chat.side_effect = ConnectionError("Ollama not running")

    with pytest.raises(RuntimeError, match="LLM extraction failed"):
        extract_action_items_llm("- Do something")
