FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY . .
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir
