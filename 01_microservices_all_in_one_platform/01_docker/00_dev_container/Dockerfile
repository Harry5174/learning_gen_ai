FROM python:3.11.7

RUN pip install poetry

WORKDIR /code/
COPY . /code/

RUN poetry install

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0"] 