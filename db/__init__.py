"""
Модуль работы с базой данных.

Содержит:
- connection.py: пул соединений PostgreSQL
- models.py: описание таблиц (SQL schemas)
- queries/: функции для работы с данными
    - users.py: get_intern, update_intern
    - answers.py: save_answer, get_answers
    - marathon.py: marathon-specific queries
    - feed.py: feed_weeks, feed_sessions
    - activity.py: activity_log, систематичность
    - qa.py: qa_history
"""
