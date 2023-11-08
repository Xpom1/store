# Store

-----

## Инструменты

- Python >= 3.9
- Django
- Django libraries
  - django-auto-prefetching
  - django-eav2
  - django-mptt
- Django Rest Framework
- Docker
- PostgreSQL
- Redis
- Celery
- Gunicorn
- Nginx

## Начало работы

Для запуска проекта на сервере следуйте инструкциям ниже.

### Предварительные требования

Убедитесь, что у вас установлены следующие инструменты:

- Docker
- Docker Compose
- Python 3.9 или выше



### Установка

Склонируйте репозиторий:

```bash
git clone https://github.com/Xpom1/store/
cd store
```

### Конфигурация

#### Настройка Django

Чтобы настроить ваш IP-адрес в Django, добавьте его в список `ALLOWED_HOSTS` в файле `settings.py`:

```python
# mystore/mystore/settings.py

ALLOWED_HOSTS = ['your_ip']
```

#### Настройка Gunicorn

Добавьте ваш IP-адрес в файл конфигурации Gunicorn.

В файле `.conf` для Gunicorn, укажите `bind`:

```conf
# Gunicorn configuration file

bind = 'your_ip:8000'
```

Не забудьте заменить `your_ip` на фактический IP-адрес вашего сервера.

#### Запустите проект с помощью Docker:
```bash
docker compose up --build
```

## Запуск тестов

Объяснение того, как запустить автоматизированные тесты для системы.

```bash
docker-compose exec web python manage.py test
```

## Настройка окружения (Локальный запуск)

Перед запуском убедитесь, что вы создали `.venv` файл с необходимыми переменными окружения, такими как ключи доступа к базе данных и другие.

#### Для Windows:
```bash
# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
.\venv\Scripts\activate

# Установка зависимостей из файла requirements.txt
pip install -r requirements.txt
```

#### Для Linux и macOS:
```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей из файла requirements.txt
pip install -r requirements.txt
```

#### Команда для запуска проекта

```bash
python3 .\mystore\manage.py runserver
```

