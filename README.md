RailStakes - Система расчета железнодорожных тарифов
Профессиональный веб-сервис для расчета железнодорожных тарифов перевозок.
Платформа позволяет сотрудникам транспортных компаний быстро и точно рассчитывать стоимость перевозки грузов между станциями с использованием актуальных тарифов через интеграцию с внешним API. Система сохраняет историю расчетов, управляет квотами пользователей и предоставляет удобный интерфейс для работы со справочниками.

Ссылка на рабочий проект: [https://rail-calc.ru]

🚀 Технологии
Python 3.13

Django 6.0

В разработке использовался BDEngine PostgreSQL

На деплое используется MySQL

Requests 2.31+ - для HTTP-запросов к внешнему API

Django Templates - для рендеринга HTML

Dotenv - для управления переменными окружения

1. Главная страница - Расчет тарифа
Интерфейс формы расчета тарифа с автодополнением станций и грузов
![alt text](image-5.png)

2. История расчетов
Страница с историей всех расчетов пользователя с отображением статуса и стоимости
![alt text](image-4.png)

3. Панель администратора
https://screenshots/admin_panel.png
Интерфейс администратора для управления справочниками
![alt text](image-1.png)
![alt text](image-2.png)
![alt text](image-3.png)



📋 Функциональность
Для пользователей:
Расчет стоимости перевозки с учетом всех параметров

Автодополнение при выборе станций и грузов

Просмотр истории своих расчетов

Отслеживание оставшегося лимита запросов

Для администраторов:
Управление пользователями и их квотами

Редактирование справочников (станции, грузы, типы вагонов)

Просмотр статистики всех расчетов



Как запустить проект локально

1. Клонируйте репозиторий:
bash
```
git clone https://github.com/BBLD10W0-1010/RailStakes
cd RailStakes
```
2. Создайте и активируйте виртуальное окружение:
bash
# Для Linux/Mac:
```
python -m venv venv
source venv/bin/activate
```
# Для Windows:
```
python -m venv venv
venv\Scripts\activate
```
3. Установите зависимости:
bash
```
pip install -U pip wheel setuptools 
pip install -r requirements.txt
#Обязательно должен быть:
#Django==4.2.*
#gunicorn
#mysqlclient
```
4. Установка и создание БД MySQL:
bash
```
sudo apt install -y mysql-server
sudo mysql
```

MySQL
```
CREATE DATABASE YOUR_NAME CHARACTER SET utf8mb4;
CREATE USER 'YOUR_NAME'@'localhost' IDENTIFIED BY 'YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON YOUR_NAME.* TO 'YOUR_NAME'@'localhost';
FLUSH PRIVILEGES;
```

Обновите в setting.py настройки DATABASE в соответствии с созданными данными

bash
```
EXIT;
```

5. Настройте переменные окружения:
Создайте файл .env в корневой директории проекта:

    ```
    DB_ENGINE=django.db.backends.postgresql // либо ваш DB_ENGINE, прим. django.db.backends.mysql

    DB_NAME=rail_stakes // название вашей бд

    DB_USER=your_username // имя пользователя бд

    DB_USER_PASSWORD=your_password // пароль пользователя бд

    DB_HOST=localhost // адрес хоста

    DB_PORT=5432 // порт хоста

    ALTA_API_BASE_URL=https://www.alta.ru/rail_tracking/rail_trf/ //оставлять таким

    ALTA_API_KEY=your_api_key_here // Ваш ключ полученный от представителей Альта-софт, 32 символа, состоит из заглавных английских букв и цифр.
    ```

6. settings.py:

Обязательные настройки для прода:

python
```
DEBUG = False

ALLOWED_HOSTS = [
    "your-domain.com",
    "www.your-domain.com",
    "SERVER_IP",
]

STATIC_URL = "/static/"
STATIC_ROOT = "/var/www/railstakes/static"
```

python
```
python manage.py collectstatic
```
Путь в конце выполнения collectstatic должен совпадать с STATIC_ROOT


7. Gunicorn (systemd)

bash
```
sudo nano /etc/systemd/system/railstakes.service
```

ini
```
[Unit]
Description=Gunicorn for RailStakes
After=network.target

[Service]
User=YOR_USER
Group=www-data
WorkingDirectory=PATH_TO_YOUR_WORKFOLDER

EnvironmentFile=PATH_TO_YOUR_ENV
Environment="PATH=PATH_TO_YOUR_VENV"

ExecStart=/root/RailStakes/venv-clean/bin/gunicorn \
  --workers 3 \
  --bind 127.0.0.1:8000 \
  RailStakes.wsgi:application

Restart=always

[Install]
WantedBy=multi-user.target
```

bash
```
sudo systemctl daemon-reload
sudo systemctl enable --now railstakes
```

8. Nginx
```
sudo nano /etc/nginx/sites-available/railstakes
```

nginx
```
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name YOUR_DOMAIN YOUR_DOMAIN2;

    location /static/ {
        alias /var/www/railstakes/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

bash
```
sudo ln -s /etc/nginx/sites-available/railstakes /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```



9. Выпуск сертификата:
bash
```
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```


10. Полезные команды:
Перезапуск приложения
bash
```
sudo systemctl restart railstakes 
```

Загрузка файлов грузов, вагонов, станций (примеры уже есть в репозитории)
bash
```
python manage.py load_references 
```
После выполнения в базе появятся записи, которых достаточно для проверки работы сайта



