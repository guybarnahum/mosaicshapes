# 
FROM python:3.8

# 
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
COPY ./boto.cfg /etc/boto.cfg

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Python
RUN python -m pip install --upgrade pip
#RUN pip install --upgrade -r /code/requirements.txt
#RUN pip install -U "celery[redis]"
RUN pip install -r /code/requirements.txt

# FastApi App
COPY ./app /code/app
COPY ./worker /code/worker
COPY ./mosaic /code/mosaic
RUN mkdir /public

ENV PYTHONPATH "${PYTHONPATH}:/code/app:/code/worker"

# Server
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
