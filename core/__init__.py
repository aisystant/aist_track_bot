"""
Ядро бота: общие компоненты.

Содержит:
- helpers.py: вспомогательные функции для генерации контента
- router.py: маршрутизация по режимам (Марафон/Лента) - TODO
- intent.py: распознавание намерений пользователя - TODO
- states.py: FSM состояния - TODO
- scheduler.py: настройка APScheduler - TODO
"""

from .helpers import (
    load_topic_metadata,
    get_search_keys,
    get_bloom_questions,
    get_personalization_prompt,
)

__all__ = [
    'load_topic_metadata',
    'get_search_keys',
    'get_bloom_questions',
    'get_personalization_prompt',
]
