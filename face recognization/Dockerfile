FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_DEBUG=True
ENV DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0
ENV DJANGO_DATABASE_NAME=/data/db.sqlite3

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        libgl1 \
        libglib2.0-0 \
        liblapack-dev \
        libopenblas-dev \
        libx11-6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python project/manage.py migrate && python project/manage.py runserver 0.0.0.0:8000"]
