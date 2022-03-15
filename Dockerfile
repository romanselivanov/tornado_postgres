FROM python:3.10.2 as tornado
ENV PYTHONBUFFERED=1
WORKDIR /app
RUN pip install poetry
COPY . .
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

EXPOSE 8000
