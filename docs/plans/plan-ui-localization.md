# План локализации UI на выбранный язык пользователя

## Статус: Готово к реализации

## Контекст

Бот поддерживает 3 языка: русский (ru), английский (en), испанский (es).
Система локализации существует в `locales.py` с функцией `t(key, lang)`.

Проблема: многие UI-строки (кнопки, сообщения, меню) всё ещё захардкожены на русском языке.

---

## Архитектура локализации

### Принцип: Централизованный словарь + строгое правило

**Строгое правило:** Ни одной пользовательской строки в коде — только через `t(key, lang)`.

### Компоненты системы

```
locales.py
├── SUPPORTED_LANGUAGES = ['ru', 'en', 'es']
├── GLOSSARY = {...}           # Глоссарий терминов (новое)
└── TRANSLATIONS = {
│       'ru': {...},
│       'en': {...},
│       'es': {...}
│   }
└── t(key, lang, **kwargs)     # Функция перевода
```

### Как работает для разных ролей

#### AI-ассистент (Claude)
1. При написании кода — проверяет существующие ключи в `locales.py`
2. Новая строка → добавляет ключ во все 3 языка
3. Никогда не пишет `await message.answer("Текст")` напрямую
4. Всегда использует `await message.answer(t('key', lang))`

#### Разработчик
```python
# 1. Получить язык пользователя
lang = intern.get('language', 'ru')

# 2. Использовать t() для любого текста
await message.answer(t('mode.marathon.activated', lang))

# 3. Параметризованные строки
await message.answer(t('progress.day', lang, day=5, total=14))
```

**Проверка на захардкоженные строки:**
```bash
grep -rn "[А-Яа-яЁё]" --include="*.py" --exclude="locales.py" .
```

#### Переводчик
1. Все строки в одном файле — `locales.py`
2. Глоссарий терминов гарантирует консистентность
3. Структура позволяет сравнивать переводы side-by-side

---

## Глоссарий терминов (GLOSSARY)

Добавить в `locales.py` — соответствие ключевых терминов из `docs/ontology.md`:

```python
GLOSSARY = {
    # Режимы
    'marathon': {'ru': 'Марафон', 'en': 'Marathon', 'es': 'Maratón'},
    'feed': {'ru': 'Лента', 'en': 'Feed', 'es': 'Feed'},

    # Контент
    'lesson': {'ru': 'Урок', 'en': 'Lesson', 'es': 'Lección'},
    'task': {'ru': 'Задание', 'en': 'Task', 'es': 'Tarea'},
    'digest': {'ru': 'Дайджест', 'en': 'Digest', 'es': 'Resumen diario'},
    'topic': {'ru': 'Тема', 'en': 'Topic', 'es': 'Tema'},

    # Действия пользователя
    'fixation': {'ru': 'Фиксация', 'en': 'Fixation', 'es': 'Fijación'},
    'answer': {'ru': 'Ответ', 'en': 'Answer', 'es': 'Respuesta'},

    # Пользователи
    'learner': {'ru': 'Ученик', 'en': 'Learner', 'es': 'Estudiante'},
    'reader': {'ru': 'Читатель', 'en': 'Reader', 'es': 'Lector'},

    # Настройки
    'difficulty': {'ru': 'Сложность', 'en': 'Difficulty', 'es': 'Dificultad'},
    'reminder': {'ru': 'Напоминание', 'en': 'Reminder', 'es': 'Recordatorio'},
    'duration': {'ru': 'Длительность', 'en': 'Duration', 'es': 'Duración'},

    # Статусы
    'active': {'ru': 'Активен', 'en': 'Active', 'es': 'Activo'},
    'paused': {'ru': 'На паузе', 'en': 'Paused', 'es': 'En pausa'},
    'completed': {'ru': 'Завершён', 'en': 'Completed', 'es': 'Completado'},
    'not_started': {'ru': 'Не начат', 'en': 'Not started', 'es': 'No iniciado'},
}
```

**Функция для получения термина:**
```python
def term(key: str, lang: str = 'ru') -> str:
    """Возвращает термин из глоссария на нужном языке"""
    if key in GLOSSARY:
        return GLOSSARY[key].get(lang, GLOSSARY[key]['ru'])
    return key
```

**Использование:**
```python
# В AI-промптах для консистентности терминов
f"Режим {term('marathon', lang)} активирован!"

# В UI
await message.answer(f"{term('marathon', lang)}: {t('mode.marathon.desc', lang)}")
```

---

## Связь с AI-генерацией

Глоссарий также используется для консистентности терминов в AI-промптах:

```python
# В system_prompt для AI
f"""
Используй следующую терминологию:
- {term('marathon', lang)} — 14-дневный курс
- {term('feed', lang)} — бесконечный режим
- {term('digest', lang)} — ежедневный материал
- {term('fixation', lang)} — личный вывод
"""
```

Это гарантирует, что AI использует те же термины, что и UI.

---

## Что уже сделано

### 1. Локализация AI-генерации (завершено)
Исправлены функции генерации контента с добавлением:
- `lang_instruction` — инструкция по языку в начале system_prompt
- `lang_reminder` — напоминание о языке в конце system_prompt
- Локализованный `user_prompt`

Затронутые файлы:
- `engines/feed/planner.py`: suggest_weekly_topics, generate_multi_topic_digest, generate_topic_content
- `bot.py`: generate_content, generate_practice_intro, generate_question
- `engines/shared/question_handler.py`: generate_answer, answer_with_context

---

## Предстоящая работа

### 2. Локализация UI-строк (оценка: ~150 строк)

#### Приоритет 1: Критические файлы

| Файл | Оценка строк | Описание |
|------|--------------|----------|
| `engines/mode_selector.py` | ~60 | Меню выбора режима, настройки Марафона/Ленты |
| `bot.py` | ~70 | Обработчики команд, FSM, сообщения об ошибках |
| `engines/feed/handlers.py` | ~20 | Обработчики Ленты |

#### Приоритет 2: Вспомогательные файлы

| Файл | Оценка строк | Описание |
|------|--------------|----------|
| `engines/feed/engine.py` | ~10 | Сообщения о статусе Ленты |
| `cmd_start.py` | ~5 | Онбординг (частично локализован) |

---

## Архитектурные решения

### Правило: Никаких пользовательских строк в коде

**НЕЛЬЗЯ:**
```python
await message.answer("Произошла ошибка. Попробуйте ещё раз.")
```

**НУЖНО:**
```python
await message.answer(t('errors.try_again', lang))
```

### Структура ключей в locales.py

```
{category}.{subcategory}.{key}

Примеры:
- mode.select_title
- mode.marathon.activated
- mode.marathon.day_progress
- mode.feed.activated
- buttons.update_profile
- buttons.reminders
- errors.generic
- errors.not_registered
```

---

## Этапы реализации

### Этап 0: Создание глоссария (1 час)
1. Добавить `GLOSSARY` в `locales.py`
2. Добавить функцию `term(key, lang)`
3. Согласовать термины с `docs/ontology.md`
4. Ревью переводов с носителем (если возможно)

### Этап 1: Аудит (1-2 часа)
1. Сканировать `mode_selector.py` на все строки
2. Сканировать `bot.py` на FSM-сообщения и ошибки
3. Составить полный список ключей
4. Проверить соответствие терминов глоссарию

### Этап 2: Добавление ключей в locales.py (2-3 часа)
1. Добавить все новые ключи для RU
2. Перевести на EN (использовать термины из глоссария)
3. Перевести на ES (использовать термины из глоссария)

### Этап 3: Рефакторинг mode_selector.py (2-3 часа)
1. Заменить все строки на `t(key, lang)`
2. Добавить получение `lang` из профиля пользователя
3. Протестировать все сценарии

### Этап 4: Рефакторинг bot.py (3-4 часа)
1. Заменить FSM fallback-сообщения (уже частично сделано)
2. Заменить сообщения в обработчиках команд
3. Заменить сообщения об ошибках

### Этап 5: Тестирование (1-2 часа)
1. Создать тестовых пользователей для каждого языка
2. Пройти все сценарии
3. Проверить корректность отображения
4. Проверить консистентность терминов

---

## Новые ключи для locales.py

### Категория: mode (режим)

```python
# Выбор режима
'mode.select_title': 'Выберите режим обучения',
'mode.current_mode': 'Текущий режим',

# Марафон
'mode.marathon.name': 'Марафон',
'mode.marathon.desc': '14-дневный курс',
'mode.marathon.activated': 'Режим Марафон активирован!',
'mode.marathon.day_progress': 'День {day} из 14 | {completed}/28 тем',
'mode.marathon.settings_title': 'Ваши настройки',
'mode.marathon.time': 'Время',
'mode.marathon.reading_time': 'На чтение',
'mode.marathon.complexity': 'Сложность',
'mode.marathon.extra_reminder': 'Доп.напоминание',
'mode.marathon.paused_info': 'Лента на паузе. Вернуться: /mode',
'mode.marathon.completed_info': 'Вы прошли марафон!',
'mode.marathon.reset_confirm': 'Вы уверены, что хотите сбросить марафон?',
'mode.marathon.reset_done': 'Марафон сброшен',

# Лента
'mode.feed.name': 'Лента',
'mode.feed.desc': 'Бесконечный режим',
'mode.feed.activated': 'Режим Лента активирован!',
'mode.feed.your_topics': 'Ваши темы',
'mode.feed.paused_info': 'Марафон на паузе. Вернуться: /mode',
'mode.feed.no_topics': 'Темы не выбраны',
```

### Категория: buttons (кнопки)

```python
'buttons.update_profile': 'Обновить данные',
'buttons.reminders': 'Напоминания',
'buttons.reset_marathon': 'Сбросить марафон',
'buttons.back': 'Назад',
'buttons.confirm': 'Подтвердить',
'buttons.both_modes': 'Оба режима',
```

### Категория: status (статусы)

```python
'status.not_started': 'Не начат',
'status.active': 'Активен',
'status.paused': 'На паузе',
'status.completed': 'Завершён',
```

### Категория: errors (ошибки)

```python
'errors.generic': 'Произошла ошибка. Попробуйте ещё раз.',
'errors.not_registered': 'Сначала пройдите регистрацию: /start',
'errors.try_later': 'Попробуйте позже.',
```

### Категория: complexity (сложность)

```python
'complexity.beginner': 'Начальный',
'complexity.basic': 'Базовый',
'complexity.advanced': 'Продвинутый',
'complexity.level_n': 'Уровень {n}',
```

---

## Затрагиваемые сценарии

- **Сценарий 02.02**: Переключение режимов (`/mode`)
- **Сценарий 01.01**: Марафон (статус, настройки)
- **Сценарий 01.02**: Лента (статус, темы)

---

## Риски и митигация

| Риск | Вероятность | Митигация |
|------|-------------|-----------|
| Пропущенные строки | Средняя | Grep по кириллице после рефакторинга |
| Сломанное форматирование | Низкая | Тестирование каждого сценария |
| Контекстные переводы | Средняя | Ревью переводов носителем |

---

## Оценка трудозатрат

| Этап | Время |
|------|-------|
| Создание глоссария | 1 час |
| Аудит | 1-2 часа |
| Добавление ключей | 2-3 часа |
| mode_selector.py | 2-3 часа |
| bot.py | 3-4 часа |
| Тестирование | 1-2 часа |
| **Итого** | **10-15 часов** |

---

---

## Процесс P-05: Локализация (новый)

### Описание процесса

Создать `docs/processes/process-05-localization.md`:

```markdown
# Процесс P-05: Локализация

## Назначение
Обеспечение корректного отображения UI и AI-контента на выбранном пользователем языке.

## Компоненты

### 1. Глоссарий терминов (GLOSSARY)
- Источник истины: `docs/ontology.md`
- Реализация: `locales.py` → `GLOSSARY`
- Функция: `term(key, lang)` → термин на нужном языке

### 2. UI-строки (TRANSLATIONS)
- Реализация: `locales.py` → `TRANSLATIONS`
- Функция: `t(key, lang, **kwargs)` → перевод строки
- Правило: ни одной пользовательской строки в коде

### 3. AI-генерация
- `lang_instruction` — в начале system_prompt
- `lang_reminder` — в конце system_prompt
- Локализованный `user_prompt`

## Диаграмма

```
Пользователь выбирает язык
         ↓
   intern['language']
         ↓
    ┌────┴────┐
    ↓         ↓
  UI-строки  AI-генерация
    ↓         ↓
  t(key,    lang_instruction +
   lang)    lang_reminder +
    ↓       user_prompt
    ↓         ↓
    └────┬────┘
         ↓
   Контент на языке пользователя
```

## Точки входа

| Файл | Функция | Что делает |
|------|---------|------------|
| `locales.py` | `t()` | Перевод UI-строк |
| `locales.py` | `term()` | Термин из глоссария |
| `bot.py` | `generate_*` | AI-генерация контента |
| `planner.py` | `suggest_*`, `generate_*` | AI-генерация для Ленты |
| `question_handler.py` | `generate_answer` | AI-ответы на вопросы |

## Инварианты

1. Все строки из `TRANSLATIONS` должны существовать для всех языков
2. Все термины из `GLOSSARY` должны существовать для всех языков
3. AI-генерация должна использовать `lang_instruction` + `lang_reminder`
4. В коде не должно быть захардкоженных пользовательских строк
```

---

## Автопроверки (tests/)

### Этап 6: Автопроверки локализации (2-3 часа)

Создать `tests/test_localization.py`:

```python
"""
Автопроверки локализации.

Запуск: pytest tests/test_localization.py -v
"""

import pytest
from locales import TRANSLATIONS, GLOSSARY, SUPPORTED_LANGUAGES, t, term


class TestTranslationsCompleteness:
    """Проверка полноты переводов"""

    def test_all_languages_have_same_keys(self):
        """Все языки должны иметь одинаковые ключи"""
        ru_keys = set(TRANSLATIONS['ru'].keys())

        for lang in SUPPORTED_LANGUAGES:
            lang_keys = set(TRANSLATIONS[lang].keys())
            missing = ru_keys - lang_keys
            extra = lang_keys - ru_keys

            assert not missing, f"[{lang}] Отсутствуют ключи: {missing}"
            assert not extra, f"[{lang}] Лишние ключи: {extra}"

    def test_no_empty_translations(self):
        """Переводы не должны быть пустыми"""
        for lang in SUPPORTED_LANGUAGES:
            for key, value in TRANSLATIONS[lang].items():
                assert value.strip(), f"[{lang}] Пустой перевод: {key}"

    def test_placeholders_match(self):
        """Плейсхолдеры {param} должны совпадать во всех языках"""
        import re
        placeholder_pattern = re.compile(r'\{(\w+)\}')

        for key in TRANSLATIONS['ru'].keys():
            ru_placeholders = set(placeholder_pattern.findall(TRANSLATIONS['ru'][key]))

            for lang in SUPPORTED_LANGUAGES:
                if lang == 'ru':
                    continue
                lang_placeholders = set(placeholder_pattern.findall(TRANSLATIONS[lang][key]))
                assert ru_placeholders == lang_placeholders, \
                    f"[{key}] Плейсхолдеры не совпадают: ru={ru_placeholders}, {lang}={lang_placeholders}"


class TestGlossaryCompleteness:
    """Проверка полноты глоссария"""

    def test_all_terms_have_all_languages(self):
        """Все термины должны иметь переводы на все языки"""
        for term_key, translations in GLOSSARY.items():
            for lang in SUPPORTED_LANGUAGES:
                assert lang in translations, f"Термин '{term_key}' не имеет перевода на {lang}"
                assert translations[lang].strip(), f"Термин '{term_key}' пустой для {lang}"


class TestNoHardcodedStrings:
    """Проверка отсутствия захардкоженных строк"""

    def test_no_cyrillic_in_code(self):
        """В коде не должно быть кириллицы (кроме locales.py и тестов)"""
        import os
        import re

        cyrillic_pattern = re.compile(r'[А-Яа-яЁё]')
        exclude_files = {'locales.py', 'test_localization.py'}
        exclude_dirs = {'__pycache__', '.git', 'docs', 'topics'}

        violations = []

        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if not file.endswith('.py') or file in exclude_files:
                    continue

                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        # Пропускаем комментарии и docstrings
                        stripped = line.strip()
                        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                            continue

                        # Ищем кириллицу в строковых литералах
                        if cyrillic_pattern.search(line) and ('"' in line or "'" in line):
                            # Проверяем, что это не импорт и не logger
                            if 'import' not in line and 'logger' not in line.lower():
                                violations.append(f"{filepath}:{line_num}: {line.strip()[:80]}")

        assert not violations, f"Найдена кириллица в коде:\n" + "\n".join(violations[:10])


class TestTFunction:
    """Проверка функции t()"""

    @pytest.mark.parametrize("lang", SUPPORTED_LANGUAGES)
    def test_t_returns_string(self, lang):
        """t() должна возвращать строку для всех языков"""
        for key in list(TRANSLATIONS['ru'].keys())[:10]:  # Первые 10 ключей
            result = t(key, lang)
            assert isinstance(result, str)
            assert result  # Не пустая

    def test_t_with_params(self):
        """t() должна подставлять параметры"""
        # Предполагаем, что есть ключ с плейсхолдером
        if 'progress.day' in TRANSLATIONS['ru']:
            result = t('progress.day', 'ru', day=5, total=14)
            assert '5' in result
            assert '14' in result

    def test_t_fallback_to_key(self):
        """t() должна возвращать ключ если перевод не найден"""
        result = t('nonexistent.key', 'ru')
        assert result == 'nonexistent.key'


class TestTermFunction:
    """Проверка функции term()"""

    @pytest.mark.parametrize("lang", SUPPORTED_LANGUAGES)
    def test_term_returns_string(self, lang):
        """term() должна возвращать строку для всех языков"""
        for key in GLOSSARY.keys():
            result = term(key, lang)
            assert isinstance(result, str)
            assert result  # Не пустая

    def test_term_fallback(self):
        """term() должна возвращать ключ если термин не найден"""
        result = term('nonexistent_term', 'ru')
        assert result == 'nonexistent_term'
```

### CI/CD интеграция

Добавить в `.github/workflows/` или pre-commit hook:

```yaml
# .github/workflows/localization.yml
name: Localization Check

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install pytest
      - run: pytest tests/test_localization.py -v
```

---

## Обновлённая оценка трудозатрат

| Этап | Время |
|------|-------|
| Создание глоссария | 1 час |
| Аудит | 1-2 часа |
| Добавление ключей | 2-3 часа |
| mode_selector.py | 2-3 часа |
| bot.py | 3-4 часа |
| Тестирование ручное | 1-2 часа |
| **Автопроверки + процесс** | **2-3 часа** |
| **Итого** | **12-18 часов** |

---

## Следующие шаги

1. Получить подтверждение плана от пользователя
2. Начать с Этапа 0 (глоссарий)
3. Реализовывать поэтапно с промежуточными коммитами
4. После завершения — создать `docs/processes/process-05-localization.md`
5. Добавить автопроверки в CI/CD
