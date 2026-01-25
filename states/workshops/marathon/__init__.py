"""
Стейты мастерской Марафон.

Содержит:
- day.py: показ урока текущего дня
- question.py: вопрос на понимание урока
- bonus.py: бонусный вопрос повышенной сложности
- task.py: практическое задание

Flow:
  day → question → [bonus*] → task → day (следующий)

  * bonus предлагается только если bloom_level < 3
"""

from .bonus import MarathonBonusState

__all__ = ['MarathonBonusState']
