FROM python:3.7-alpine
ARG commit=""

LABEL maintainer="Erik <erikvlilja+syex@gmail.com>"

RUN mkdir /app

COPY pyproject.toml /app/
COPY poetry.lock /app/

WORKDIR /app


# install poetry, dependencies, then remove poetry
RUN apk add --no-cache libressl-dev musl-dev libffi-dev gcc
RUN pip --no-cache-dir install poetry poetry-setup \
    && poetry install \
    && rm -rf ~/.config/pypoetry

COPY . /app

EXPOSE 8080

CMD ["poetry", "run", "python", "/app/app.py"]
