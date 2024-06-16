FROM python:3.8.6

# рабочая директория внутри проекта
WORKDIR /usr/src/app

# переменные окружения для python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# копируем содержимое текущей папки в контейнер
COPY . .

RUN apt-get update && apt-get install -y \ 
    libfreetype6-dev \ 
    libpng-dev \ 
    libjpeg-dev \ 
    && rm -rf /var/lib/apt/lists/* 
 
RUN pip install --upgrade pip setuptools 
RUN pip install -r requirements.txt 
RUN pip install KlAkOAPI-14.tar.gz 
 
ENV http_proxy "" 
ENV https_proxy ""

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
