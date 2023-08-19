FROM python:3.11.4-alpine3.17

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV TZ=Asia/Bishkek

RUN apk add --no-cache gcc \
    gettext linux-headers musl-dev make \
    python3-dev libffi-dev openssl-dev cargo \
    && rm -rf /var/apt/list/*

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8081

ENTRYPOINT ["sh", "./docker_entrypoint.sh"]
