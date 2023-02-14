# 
FROM python:3.8

# 
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt

# Python
RUN python -m pip install --upgrade pip
RUN pip install --upgrade -r /code/requirements.txt

# FastApi App
COPY ./app /code/app
ENV PYTHONPATH "${PYTHONPATH}:/code/app"

# Server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
