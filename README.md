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

___
#### Примеры запросов и ответов
_1) POST /api/statistics_ - метод сохранения статистики \
Тело запроса (пример):
```json
{
  "date": "2020-01-01",
  "views": 0,
  "clicks": 0,
  "cost": 0
}
```
Описание параметров:
- _date_ - дата события, тип данных datetime.date (обязательный параметр);
- _views_ - количество показов, тип данных int (неотрицательный, необязательный параметр, по умолчанию 0);
- _clicks_ - количество кликов, тип данных int (неотрицательный, необязательный параметр, по умолчанию 0);
- _cost_ - стоимость кликов, тип данных float (неотрицательный, необязательный параметр, по умолчанию 0).

Примеры использования:
1. Сохранение нового события (за указанную дату статистики еще нет). \
    Запрос:
    ```json
    {
      "date": "2022-01-01",
      "views": 200,
      "clicks": 400,
      "cost": 100
    }
    ```
    Ответ: \
    ![post_1](https://github.com/MaksimBoltov/statistics-counter-service/raw/main/docs/screenshots/post_1.png)
    
    Поле _created_ указывает на то, было ли создано событие
    (если True - событие было создано для данной даты,
    если False - данные по событию были обновлены). Поле _aggregated_ указывает, было ли событие обновлено
    (если True - данные по событию были обновлены, если False - событие было создано).

2. Сохранение события за существующую дату (за указанную дату статистика уже присутствует). \
    Запрос:
    ```json
    {
      "date": "2022-01-01",
      "views": 100,
      "clicks": 500,
      "cost": 200
    }
    ```
    Ответ: \
    ![post_2](https://github.com/MaksimBoltov/statistics-counter-service/raw/main/docs/screenshots/post_2.png)
    
    Из ответа видно, что теперь не создается новый объект в базе данных, а обновляется уже имеющийся
    (_created_ = False, _aggregated_ = True). При этом параметры отправленные в запросе суммируются с теми,
    что уже записаны в базу данных.

3. Сохранение события с не польностью заполненными данными (пропущены опционные параметры). \
    Запрос:
    ```json
    {
      "date": "2022-02-01",
      "views": 1000
    }
    ```
    Ответ: \
    ![post_3](https://github.com/MaksimBoltov/statistics-counter-service/raw/main/docs/screenshots/post_3.png)
    
    Данные прошли валидацию и вмето пропущенных параметров были записаны значения 0.
    Поскольку за 2022-02-01 еще не было добавлено событий, то _created_ = True.
    
4. Сохранение события с неверно введенными данными (ошибка валидации). \
    Запрос:
    ```json
    {
      "date": "2022-02-01",
      "views": 1000
    }
    ```
    Ответ: \
    ![post_4](https://github.com/MaksimBoltov/statistics-counter-service/raw/main/docs/screenshots/post_4.png)
    
    Данные не прошли валидацию, из-за чего pydantic выдает ошибку.

\
_2) GET /api/statistics_ - метод показа статистики \
Пример запроса: \
_/api/statistics?date_from=2022-01-01&date_to=2022-02-01&sort_by=date&reverse_sort=false'_

Описание параметров:
- _date_from_ - дата, начиная с которой (включительно) отображать статистику, формат даты YYYY-MM-DD
(опционный параметр, по умолчанию ограничения слева нет);
- _date_to_ - дата, заканчивая которой (включительно) отображать статистику, формат даты YYYY-MM-DD
(опционный параметр, по умолчанию ограничения справа нет);
- _sort_by_ - поле, по которому необходимо отсортировать выходные данные (опционный параметр, по умолчанию
(а также при неверном значении параметра) выполняется сортировка по полю _date_);
- _reverse_sort_ - объявляет, необходимо ли сортировать в обратном порядке, тип bool (опционный, по умолчанию False).

Примеры использования (для примера была создана статистика за 3 для с 2022-01-01 по 2022-01-03):
1. Отображение статистики без указания параметров. \
    Запрос:
    _/api/statistics_
    
    Ответ: \
    ![get_1](https://github.com/MaksimBoltov/statistics-counter-service/raw/main/docs/screenshots/get_1.png)
    
    Данные выводятся в виде словаря для удобного поиска по дате.
    В элемент статистики также добавляются параметры:
    - _cpc_ - средняя стоимость клика, которая расчитывается: `cost/clicks`
    - _cpm_ - средняя стоимость 1000 показов, которая расчитывается: `cost/views * 1000`
    
    Статистика по умолчанию отсортирована по полю _date_.

2. Отображение статистики c сортировкой по полю _cpm_. \
    Запрос:
    _/api/statistics?sort_by=cpm_
    
    Ответ: \
    ![get_2](https://github.com/MaksimBoltov/statistics-counter-service/raw/main/docs/screenshots/get_2.png)
    
    Статистика отсортирована по полю _cpm_ по возрастанию значения.

3. Отображение статистики c сортировкой по полю _cpm_ в обратном порядке. \
    Запрос:
    _/api/statistics?sort_by=cpm&reverse_sort=true_
    
    Ответ: \
    ![get_3](https://github.com/MaksimBoltov/statistics-counter-service/raw/main/docs/screenshots/get_3.png)
    
    Статистика отсортирована по полю _cpm_ по убыванию значения (в обратном порядке).

4. Отображение статистики c фильтрацией с использованием параметра _date_from_. \
    Запрос:
    _/api/statistics?date_from=2022-01-02_
    
    Ответ: \
    ![get_4](https://github.com/MaksimBoltov/statistics-counter-service/raw/main/docs/screenshots/get_4.png)
    
    В выходные данные не включена статистика за 2022-01-01.

5. Отображение статистики c фильтрацией с использованием параметра _date_to_. \
    Запрос:
    _/api/statistics?date_to=2022-01-02_
    
    Ответ: \
    ![get_5](https://github.com/MaksimBoltov/statistics-counter-service/raw/main/docs/screenshots/get_5.png)
    
    В выходные данные не включена статистика за 2022-01-03.

6. Отображение статистики c фильтрацией с использованием параметров _date_from_ и _date_to_. \
    Запрос:
    _/api/statistics?date_from=2022-01-02&date_to=2022-01-02_
    
    Ответ: \
    ![get_6](https://github.com/MaksimBoltov/statistics-counter-service/raw/main/docs/screenshots/get_6.png)
    
    В выходные данные не включена статистика за 2022-01-01 и 2022-01-03.

7. Отображение статистики c фильтрацией и сортировкой. \
    Запрос:
    _/api/statistics?date_from=2022-01-01&date_to=2022-01-02&sort_by=cost&reverse_sort=true_
    
    Ответ: \
    ![get_7](https://github.com/MaksimBoltov/statistics-counter-service/raw/main/docs/screenshots/get_7.png)
    
    Выходные данные отфильтрованы по обоим промежуткам, таким образом не попала статистика за 2022-01-03.
    Также данные отсортированы по полю _cost_ в обратном порядке (поле _reverse_sort=true_).
    
\
_3) DELETE /api/statistics_ - метод сброса статистики \
    Запрос не принимает никаких параметров. \
    Пример запроса через curl: \
    ```curl -X 'DELETE' 'http://127.0.0.1:8080/api/statistics' -H 'accept: application/json'``` \
    Ответ сервера: \
    ![delete_1](https://github.com/MaksimBoltov/statistics-counter-service/raw/main/docs/screenshots/delete_1.png)
    \
    После этого вся статистика, хранимая в базе данных была удалена, база данных очищена.
    
  
    