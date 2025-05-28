Это RESTful API, построенное на Django REST Framework, для управления информацией о горных перевалах. API позволяет создавать, просматривать, обновлять и удалять записи о перевалах, а также управлять связанными данными (координаты, пользователи, изображения).

## Содержание

1. [Требования](#требования)
2. [Установка](#установка)
4. [Использование API](#использование-api)
   - [Получение данных](#получение-данных)
   - [Создание перевала](#создание-перевала)
   - [Обновление перевала](#обновление-перевала)
   - [Удаление перевала](#удаление-перевала)
5. [Модели данных](#модели-данных)


## Требования

- Python 3.9+
- Django 4.0+
- Django REST Framework 3.12+
- PostgreSQL (рекомендуется)

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd project-directory 
```
2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate  # Windows
```
3. Установите зависимости:
```bash
pip install -r requirements.txt
```
4. Примените миграции:
```bash
python manage.py migrate
```
5. Запустите сервер:
```bash
python manage.py runserver
```

## Использование API
### Получение данных

GET /api/submitData/ - Получить список всех перевалов \
GET /api/submitData/?user__email=email@example.com - Фильтр по email пользователя \'
GET /api/submitData/{id} - Получить конкретный перевал

Пример ответа:
```json
{
    "id": 1,
    "title": "Перевал Дятлова",
    "beauty_title": "Пер.",
    "other_titles": "Дятлова пер.",
    "connect": "",
    "add_time": "2023-01-15T10:00:00Z",
    "status": "new",
    "coord_id": 1,
    "added_user": 1,
    "winter": "1A",
    "summer": "1B",
    "autumn": "1A",
    "spring": "1A"
}
```

### Создание перевала

POST /api/submitData/{id}

Пример тела запроса:
```json
{
    "user": {
        "email": "user@example.com",
        "name": "Иван",
        "fam": "Иванов",
        "otc": "Иванович",
        "phone": "+79991234567"
    },
    "coords": {
        "latitude": "45.3842",
        "longitude": "7.1525",
        "height": "1200"
    },
    "level": {
        "winter": "1A",
        "summer": "1B",
        "autumn": "1A",
        "spring": "1A"
    },
    "images": [
        {
            "data": "base64_encoded_image_1",
            "title": "Вид с севера"
        },
        {
            "data": "base64_encoded_image_2",
            "title": "Вид с юга"
        }
    ],
    "title": "Перевал Дятлова",
    "beauty_title": "Пер.",
    "other_titles": "Дятлова пер.",
    "connect": ""
}
```

### Обновление перевала

PATCH /api/submitData/{id}

Ограничения:
* Только для статуса "new"
* Нельзя изменять пользователя

Пример тела запроса:
```json
{
    "coords": {
        "latitude": "45.3842",
        "longitude": "7.1525",
        "height": "1250"
    },
    "level": {
        "winter": "2A"
    }
}
```

### Удаление перевала

DELETE /api/submitData/{id}

### Модели данных
Основные модели:
* Pereval - информация о перевале
* Users - данные пользователя
* Coords - географические координаты
* Image - изображения перевала