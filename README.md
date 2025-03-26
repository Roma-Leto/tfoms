# Приложение анализа счетов

## Установка 

0. Виртуальное окружение
```bash
python venv .venv
source .venv/bin/activate
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
celery -A x_tfoms_project worker -l INFO
```

Подключение и проверка работы Redis
```bash
docker exec -it redis redis-cli
set key 'hello'
get key
exit
```

Узнать адрес Docker-контейнера Redis
```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' redis
```

Запуск проекта Django
```bash
python manage.py runserver 0.0.0.0:8000
```

Админ-панель
```bash
http://127.0.0.1:8000/admin/
```

Git
```bash
https://github.com/Roma-Leto/tfoms
https://github.com/Roma-Leto/tfoms.git
```