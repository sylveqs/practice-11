# Task Manager API

Backend для системы управления задачами (Task Manager), позволяющей пользователям создавать проекты и управлять задачами внутри них. Разработан на FastAPI с использованием SQLite, JWT аутентификацией и SQLAlchemy 2.0+ с современным синтаксисом.

## 📋 Содержание

- [Технологический стек](#технологический-стек)
- [Функциональность](#функциональность)
- [Установка и запуск](#установка-и-запуск)
- [Структура проекта](#структура-проекта)
- [API Эндпоинты](#api-эндпоинты)
- [Модели данных](#модели-данных)
- [Аутентификация](#аутентификация)
- [Миграции базы данных](#миграции-базы-данных)
- [Примеры запросов](#примеры-запросов)
- [Обработка ошибок](#обработка-ошибок)
- [Переменные окружения](#переменные-окружения)
- [Развертывание](#развертывание)

## 🛠 Технологический стек

- **FastAPI** - современный веб-фреймворк для создания API
- **SQLite3** - легковесная база данных
- **SQLAlchemy 2.0+** - ORM с современным синтаксисом (Mapped / mapped_column)
- **JWT (python-jose)** - JSON Web Tokens для аутентификации
- **Alembic** - инструмент для миграций базы данных
- **Bcrypt (passlib)** - хеширование паролей
- **Pydantic v2** - валидация данных и управление настройками

## ✨ Функциональность

### Пользователи и аутентификация
- ✅ Регистрация новых пользователей с уникальными email и username
- ✅ Вход в систему с получением JWT токена (срок действия - 1 час)
- ✅ Защита паролей с помощью bcrypt хеширования
- ✅ Выход из системы (удаление токена на клиенте)

### Проекты
- ✅ Создание проектов с названием и описанием
- ✅ Просмотр списка всех проектов пользователя
- ✅ Подсчет количества задач в каждом проекте
- ✅ Просмотр детальной информации о проекте со всеми задачами
- ✅ Сортировка проектов по дате создания (новые сверху)

### Задачи
- ✅ Создание задач внутри проектов
- ✅ Назначение исполнителей задач (опционально)
- ✅ Три статуса задач: "todo", "in_progress", "done"
- ✅ Просмотр всех задач проекта
- ✅ Частичное обновление задач (PATCH)
- ✅ Удаление задач
- ✅ Автоматическое обновление поля updated_at при изменениях

### Безопасность и права доступа
- ✅ Все эндпоинты (кроме регистрации и логина) защищены JWT
- ✅ Проверка прав доступа: пользователь может управлять только своими проектами
- ✅ Каскадное удаление задач при удалении проекта

## 🚀 Установка и запуск

### Предварительные требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)
- virtualenv (рекомендуется)

### Пошаговая установка

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/yourusername/task-manager-api.git
cd task-manager-api
```

2. **Создайте и активируйте виртуальное окружение:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Создайте файл `.env` с настройками:**
```env
# Database
DATABASE_URL=sqlite:///./task_manager.db

# JWT Settings
SECRET_KEY=your-super-secret-key-change-in-production-2024
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

5. **Инициализируйте Alembic и создайте миграции:**
```bash
# Инициализация Alembic (если еще не сделано)
alembic init alembic

# Создание первой миграции
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head
```

6. **Запустите сервер:**
```bash
python run.py
```

Сервер будет доступен по адресу: `http://localhost:8000`

### Доступ к документации

- **Документация Swagger**: http://localhost:8000/docs
- **Документация ReDoc**: http://localhost:8000/redoc
- **Главная страница API**: http://localhost:8000

## 📁 Структура проекта

```
task-manager-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Главный файл приложения
│   ├── models.py               # SQLAlchemy модели (Mapped стиль)
│   ├── schemas.py              # Pydantic схемы v2
│   ├── database.py             # Конфигурация базы данных
│   ├── auth.py                 # Функции аутентификации
│   ├── config.py               # Настройки приложения
│   ├── dependencies.py         # Зависимости FastAPI
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py             # Роутер аутентификации
│   │   ├── projects.py         # Роутер проектов
│   │   └── tasks.py            # Роутер задач
│   └── alembic/                 # Миграции Alembic
│       ├── versions/
│       └── env.py
├── alembic.ini                  # Конфигурация Alembic
├── requirements.txt             # Зависимости проекта
├── .env                         # Переменные окружения
├── run.py                       # Скрипт для запуска
└── README.md                    # Документация
```

## 📚 API Эндпоинты

### Аутентификация (Auth)

| Метод | Эндпоинт | Описание | Требуется JWT |
|-------|----------|----------|---------------|
| POST | `/auth/register` | Регистрация нового пользователя | Нет |
| POST | `/auth/login` | Вход в систему, получение JWT токена | Нет |
| POST | `/auth/logout` | Выход из системы | Да |

### Проекты (Projects)

| Метод | Эндпоинт | Описание | Требуется JWT |
|-------|----------|----------|---------------|
| GET | `/projects/` | Получение списка всех проектов пользователя | Да |
| POST | `/projects/` | Создание нового проекта | Да |
| GET | `/projects/{project_id}` | Получение детальной информации о проекте | Да |

### Задачи (Tasks)

| Метод | Эндпоинт | Описание | Требуется JWT |
|-------|----------|----------|---------------|
| GET | `/projects/{project_id}/tasks` | Получение всех задач проекта | Да |
| POST | `/projects/{project_id}/tasks` | Создание новой задачи в проекте | Да |
| PATCH | `/tasks/{task_id}` | Частичное обновление задачи | Да |
| DELETE | `/tasks/{task_id}` | Удаление задачи | Да |

## 📊 Модели данных

### User (Пользователь)
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "created_at": "2024-01-01T12:00:00"
}
```

### Project (Проект)
```json
{
  "id": 1,
  "name": "Редизайн сайта",
  "description": "Обновление дизайна главной страницы",
  "owner_id": 1,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00",
  "task_count": 5
}
```

### Task (Задача)
```json
{
  "id": 1,
  "title": "Разработать макет",
  "description": "Создать Figma макет главной страницы",
  "status": "in_progress",
  "project_id": 1,
  "assignee_id": 2,
  "assignee_username": "jane_doe",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T14:30:00"
}
```

## 🔐 Аутентификация

API использует JWT (JSON Web Tokens) для аутентификации. После успешного входа вы получаете токен, который необходимо включать в заголовки всех защищенных запросов:

```
Authorization: Bearer <your_jwt_token>
```

### Срок действия токена
- Токен действителен в течение 1 часа (настраивается в `.env`)
- По истечении срока необходимо получить новый токен через `/auth/login`

## 🔄 Миграции базы данных

### Создание новой миграции
```bash
alembic revision --autogenerate -m "Описание изменений"
```

### Применение миграций
```bash
alembic upgrade head
```

### Откат миграции
```bash
alembic downgrade -1  # Откат на одну версию назад
alembic downgrade base  # Полный откат
```

### Просмотр истории миграций
```bash
alembic history
```

### Текущая версия
```bash
alembic current
```

## 📝 Примеры запросов

### Регистрация пользователя
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john_doe",
    "password": "securepassword123"
  }'
```

**Ответ (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "created_at": "2024-01-01T12:00:00"
}
```

### Вход в систему
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

**Ответ (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Создание проекта (требуется JWT)
```bash
curl -X POST "http://localhost:8000/projects/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Редизайн сайта",
    "description": "Обновление дизайна главной страницы"
  }'
```

### Получение списка проектов
```bash
curl -X GET "http://localhost:8000/projects/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Ответ (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Редизайн сайта",
    "description": "Обновление дизайна главной страницы",
    "owner_id": 1,
    "created_at": "2024-01-01T12:00:00",
    "updated_at": null,
    "task_count": 3
  }
]
```

### Создание задачи в проекте
```bash
curl -X POST "http://localhost:8000/projects/1/tasks" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Разработать макет",
    "description": "Создать Figma макет главной страницы",
    "assignee_id": 2
  }'
```

### Обновление задачи (частичное)
```bash
curl -X PATCH "http://localhost:8000/tasks/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "assignee_id": 3
  }'
```

### Удаление задачи
```bash
curl -X DELETE "http://localhost:8000/tasks/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Ответ:** `204 No Content`

## ⚠️ Обработка ошибок

API возвращает стандартные HTTP статусы с понятными сообщениями:

| Код | Описание | Пример ответа |
|-----|----------|---------------|
| 400 | Bad Request - неверные входные данные | `{"detail": "Email or username already registered"}` |
| 401 | Unauthorized - отсутствует или невалидный JWT | `{"detail": "Invalid authentication credentials"}` |
| 403 | Forbidden - недостаточно прав | `{"detail": "Not enough permissions. You are not the owner of this project"}` |
| 404 | Not Found - ресурс не найден | `{"detail": "Project not found"}` |
| 500 | Internal Server Error - внутренняя ошибка | `{"detail": "Internal server error"}` |

## 🔧 Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `DATABASE_URL` | URL подключения к БД | `sqlite:///./task_manager.db` |
| `SECRET_KEY` | Секретный ключ для JWT | `your-super-secret-key-change-in-production` |
| `ALGORITHM` | Алгоритм шифрования JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена (в минутах) | `60` |

## 🚀 Развертывание

### Для разработки
```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск с автоматической перезагрузкой
python run.py
```

### Для продакшена
```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск без автоматической перезагрузки
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🧪 Тестирование API с помощью Swagger

После запуска сервера откройте браузер и перейдите по адресу `http://localhost:8000/docs`. Вы увидите интерактивную документацию Swagger, где можете:

- Просматривать все доступные эндпоинты
- Тестировать API прямо в браузере
- Видеть схемы запросов и ответов
- Авторизоваться с помощью JWT токена (кнопка "Authorize")

## 📈 Особенности реализации

### SQLAlchemy 2.0+ (Mapped стиль)
```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    username: Mapped[str] = mapped_column(String, unique=True)
```

### Pydantic v2 валидация
```python
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(todo|in_progress|done)$")
```

### Зависимости для проверки прав
```python
def get_project_or_404(project_id: int, db: Session, current_user: User) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return project


```bash
# Клонирование и установка
git clone https://github.com/yourusername/task-manager-api.git
cd task-manager-api
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt

# Настройка базы данных
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# Запуск
python run.py
```

После выполнения этих команд API будет доступно по адресу `http://localhost:8000` 🎉

C:\Users\Sveta\Pictures\Screenshots
---
