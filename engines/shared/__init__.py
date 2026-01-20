"""
Общие компоненты для всех режимов.

Содержит:
- question_handler.py: обработка вопросов пользователя
  (работает в любом режиме, использует MCP + контекст)
"""

from .question_handler import (
    handle_question,
    search_mcp_context,
    generate_answer,
    answer_with_context,
)

__all__ = [
    'handle_question',
    'search_mcp_context',
    'generate_answer',
    'answer_with_context',
]
