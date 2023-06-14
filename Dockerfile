# base image
FROM python:3.9-slim

#maintainer
LABEL Author="Daniel Tesfai"


# The environment variable ensures that the python
# output to the terminal without buffering it first
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# switch to the app directory so that everything runs from here
COPY . /app/
COPY requirements.txt /app/
WORKDIR /app/


# #installs the requirements
RUN pip install -r requirements.txt
EXPOSE 8000
CMD python ./src/manage.py runserver 0.0.0.0:8000


