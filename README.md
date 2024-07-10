# Информационная система Орловского юридического института

## Возможности:

1. Модули для работы с системой автоматизации учебного процесса Апекс-ВУЗ:
   - **Расписание** - выгрузка расписания преподавателя (iCal, xlsx).
   - **Нагрузка** - формирование отчета о нагрузке за месяц / семестр.
   - **Учебные планы** - работа с компетенциями и их индикаторами.
   - **Программы** - проверка заполнения полей рабочих программ.
   - **Обеспечение** - загрузка обеспечивающих материалов в рабочие программы.
2. Система учета личного состава
3. Система расчета денежного содержания

![Title Screen](https://github.com/john-neg/orel-inst-system/assets/25820535/198e43a7-30ca-48fd-b9fa-044336524113)

## Tech
Python >= 3.10, Flask, SQLAlchemy, MongoDB, Docker

## Инструкция по установке (Ubuntu 22.04)

### Создаем файл с ключами доступа

```sh
cp .env.example .env
```
Добавляем URL, токен для API Апекс-ВУЗ, данные для LDAP авторизации, данные для подключения к внешней БД
```sh
nano .env
```

### Docker

```sh
cd infra
```

```sh
docker compose up
```

### Локальная установка

<details>
   <summary>
      см. действия
   </summary>

```sh
sudo apt update -y && sudo apt upgrade -y
```

добавляем RU UFT-8
```sh
dpkg-reconfigure locales
```

```sh
sudo update-locale LANG=en_US.UTF-8
```

```sh
sudo timedatectl set-timezone Europe/Moscow
```

```sh
sudo useradd -g www-data www-user
```

```sh
sudo passwd www-user
```
```sh
sudo mkdir /var/www
```
```sh
sudo usermod -d /var/www www-user
```
```sh
sudo chown -R www-user:www-data /var/www
```
```sh
sudo usermod -aG sudo www-user
```
```sh
sudo chsh -s /bin/bash www-user
```

Заходим под новым пользователем

### Git

```sh
sudo apt install git
```

```sh
ssh-keygen -t ed25519 -C git-account-e-mail
```

```sh
eval `ssh-agent -s`
```

```sh
ssh-add ~/.ssh/id_ed25519
```

Добавляем ключ из файла id_ed25519.pub в аккаунт на GitHub

```sh
cd /var/www
```

```sh
git init
```

```sh
git clone git@github.com:git-account-name/apeks-vuz-extension.git
```

### Venv

```sh
cd apeks-vuz-extension
```

```sh
sudo apt install python3.10-venv
```

```sh
python3 -m venv venv
```

```sh
source venv/bin/activate
```

### PIP

```sh
python -m pip install --upgrade pip
```

```sh
pip install wheel
```

```sh
pip install -r requirements.txt
```

```sh
pip install gunicorn
```

#### Database

Создание автомиграций базы данных
```sh
python alembic revision --autogenerate -m "Added some tables"
```

```sh
alembic upgrade head
```

```sh
python /tools/fill_db_base_users_data.py
```

```sh
deactivate
```

### Настройка системы

```sh
sudo nano /etc/systemd/system/apeks.service
```

Копируем содержимое 
(количество workers соответствует количеству cpu)
```
[Unit]
Description=Gunicorn instance to serve apeks-vuz-extension
After=network.target

[Service]
User=www-user
Group=www-data
WorkingDirectory=/var/www/apeks-vuz-extension
Environment="PATH=/var/www/apeks-vuz-extension/venv/bin"
ExecStart=/var/www/apeks-vuz-extension/venv/bin/gunicorn --workers 2 --timeout 200 --bind unix:apeks.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

```sh
sudo systemctl start apeks
```

```sh
sudo systemctl enable apeks
```

```sh
systemctl status apeks
```

### Nginx

```sh
sudo apt install nginx
```

```sh
sudo ufw app list
```

```sh
sudo ufw allow 'Nginx HTTP'
```

```sh
sudo ufw status
```

```sh
systemctl status nginx
```

```sh
sudo nano /etc/nginx/nginx.conf
```

Добавляем:
```
client_max_body_size 20M;
```

```sh
sudo nano /etc/nginx/sites-available/apeks
```

Копируем содержимое
```
server {
    listen 80;
    server_name 0.0.0.0;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/apeks-vuz-extension/apeks.sock;
    }
}
```

```sh
sudo nano /etc/nginx/proxy_params
```

Копируем содержимое
```
proxy_set_header Host $http_host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_connect_timeout   180;
proxy_send_timeout      180;
proxy_read_timeout      180;
```

```sh
sudo ln -s /etc/nginx/sites-available/apeks /etc/nginx/sites-enabled
```

Удаляем default из /etc/nginx/sites-enabled

```sh
sudo rm /etc/nginx/sites-enabled/default
```

Проверяем конфигурацию
```sh
sudo nginx -t
```

Перезапускаем сервер
```sh
sudo systemctl restart nginx
```
</details>