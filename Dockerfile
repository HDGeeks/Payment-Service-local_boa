
FROM python:3.8-slim

COPY ./requirements.txt /requirements.txt
COPY ./src /app
WORKDIR /app

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /requirements.txt && \
    /py/bin/python manage.py makemigrations && \
    /py/bin/python manage.py makemigrations gift && \
    /py/bin/python manage.py makemigrations subscription && \
    /py/bin/python manage.py makemigrations telebirr && \
    /py/bin/python manage.py migrate gift && \
    /py/bin/python manage.py migrate subscription && \
    /py/bin/python manage.py migrate telebirr && \
    /py/bin/python manage.py migrate --run-syncdb && \
    /py/bin/python manage.py collectstatic --no-input

ENV PATH="/py/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

CMD exec gunicorn --bind 0.0.0.0:8000 --workers 1 --threads 8 --timeout 0 core.wsgi:application