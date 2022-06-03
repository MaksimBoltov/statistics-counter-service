# Statistics counter service
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/MaksimBoltov/statistics-counter-service.svg?logo=python&logoWidth=13)](https://lgtm.com/projects/g/MaksimBoltov/statistics-counter-service/context:python)
[![codecov](https://codecov.io/gh/MaksimBoltov/statistics-counter-service/branch/main/graph/badge.svg?token=Rmrvo3iT7v&style=plastic)](https://codecov.io/gh/MaksimBoltov/statistics-counter-service)

#### Краткое описание 
Проект представляет собой сервис ведения статистики и содержит методы:
- сохранение статистики (обновление в случае наличия статистики за указанную дату)
- просмотр статистики с возможностью фильтрации по дате и сортировки по всем полям
- сброс всей накопившейся статистики

#### Стек технологий
- Python
- FastAPI
- PostgreSQL
- SQLAlchemy, Alembic
- Docker
____

#### Запуск и использование
Запустить проект можно в Docker. Для этого необходимо выполнить следующие команды:
1. Запустить на сборку docker-образ в фоновом режиме:
    ```shell script
    $ docker-compose up -d --build
    ```
2. Применить миграции к базе данных для создания таблиц:
    ```shell script
    $ docker-compose exec web alembic upgrade head
    ```
После этого проект станет доступен по адресу http://127.0.0.1:8080 \
Для просмотра документации и ознакомления с функционалом:\
http://127.0.0.1:8080/docs