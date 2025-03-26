FROM python:3.12-alpine

ARG CRON="00 06 * * *"

RUN apk add poetry

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN poetry install

COPY . .

RUN crontab -l | { cat; echo "${CRON}  poetry run -C /app python /app/main.py"; } | crontab -

CMD ["crond", "-f", "-l", "2"]