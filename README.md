# Приложение анализа счетов

## Установка 

0. Виртуальное окружение
```bash
python venv .venv
```

1. Пакеты для виртуального окружения
```bash
pip install pytest hypothesis pandas openpyxl channels[daphne]
pip install -U "celery[redis]"
pip install redis celery django_bootstrap5 django pyodbc mssql-django
```
or
```bash
pip install -r requirements.txt 
```

2. Миграции
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Установка драйвера MS SQL для Astra Linux
```bash
sudo apt-get install unixodbc-dev 
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install msodbcsql17
```

4. Create superuser
```bash
python manage.py createsuperuser 
```
5. Удаление .idea из git
```bash
git rm --cached .idea -rf
```

6. Запуск Redis (контейнер Docker)
```bash
sudo docker start redis
```

Подключение и проверка работы Redis
```bash
docker exec -it redis redis-cli
set key 'hello'
get key
exit
```