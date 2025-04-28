# Проект анализа новостей о политиках (с сентября 2024 года)

## Описание проекта

Проект собирает и анализирует новостные статьи о мировых политиках: **Xi Jinping**, **Donald Trump** и **Vladimir Putin** с 1 сентября 2024 года. Новости извлекаются из RSS-лент ведущих мировых СМИ и через NewsAPI. Данные хранятся в SQLite и экспортируются в CSV. Выполняется анализ частоты упоминаний и тональности новостей, результаты визуализируются.

## Структура проекта

```
project/
├── main.py                    # Основной модуль запуска проекта
├── rss_feeds.py               # Список RSS-источников
├── rss.py                     # Функции для парсинга RSS
├── api_fetcher.py             # Сбор данных через NewsAPI
├── database_utils.py          # Работа с SQLite
├── sentiment_analysis.py      # Анализ тональности (DistilBERT)
├── analyze.py                 # Построение графиков и анализ
├── requirements.txt           # Зависимости проекта
├── news.db                    # БД SQLite (создаётся автоматически)
├── timeseries.csv             # CSV с результатами (создаётся автоматически)
└── graphs/                    # Папка для графиков (создаётся автоматически)
```

## Файлы и их назначение
- **`main.py`** – основной запускаемый скрипт.
- **`rss_feeds.py`** – словарь RSS-источников.
- **`rss.py`** – загрузка новостей из RSS.
- **`api_fetcher.py`** – взаимодействие с NewsAPI.
- **`database_utils.py`** – работа с базой SQLite.
- **`sentiment_analysis.py`** – анализ тональности новостей.
- **`analyze.py`** – генерация и сохранение графиков.

## Как запустить проект в Google Colab

### 1. Клонируйте репозиторий
```bash
!git clone https://github.com/yourusername/your-repo.git
%cd your-repo
```

### 2. Установите зависимости
```python
!pip install -r requirements.txt
```

### 3. Настройка параметров
- Установите API-ключ от [NewsAPI.org](https://newsapi.org/):
```python
import os
os.environ['NEWSAPI_KEY'] = "ВАШ_API_КЛЮЧ"
```
- Измените переменную `OUT_DIR` в `main.py` на нужный путь (например, Google Drive).
- Проверьте дату начала сбора новостей (`CUTOFF_DATE = datetime(2024, 9, 1)`).

### 4. Запустите сбор и анализ
```python
from main import one_cycle
one_cycle()
```

## Просмотр результатов
После выполнения в указанной папке вы найдёте:
- Файл `news.db` с новостями (SQLite)
- Файл `timeseries.csv` (количество упоминаний)
- Графики (`*.png`) в папке `graphs`

## Визуализации
- **Ежедневный, недельный и месячный тренды** упоминаний политиков.
- **Тренды тональности новостей** (позитивные и негативные).
- **Топ-источники** по количеству публикаций для каждого политика.

Для просмотра графиков используйте любой просмотрщик изображений или добавьте в код блок:
```python
from IPython.display import Image, display
import os

graphs_path = 'graphs/'
for graph in os.listdir(graphs_path):
    display(Image(filename=os.path.join(graphs_path, graph)))
```



