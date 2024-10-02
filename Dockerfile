# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.10.12

FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ARG UID=1000

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libxml2-dev \
        libxslt1-dev \
        antiword \
        unrtf \
        poppler-utils \
        pstoedit \
        tesseract-ocr \
        flac \
        ffmpeg \
        lame \
        libmad0 \
        libsox-fmt-mp3 \
        sox \
        libjpeg-dev \
        swig \
        libpulse-dev \
        jq && \
    rm -rf /var/lib/apt/lists/* && \
    adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser && \
    pip install --no-cache-dir --upgrade pip

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

#COPY entrypoint.sh /entrypoint.sh
#RUN chmod +x /entrypoint.sh

USER appuser

WORKDIR /app

COPY . .

ENTRYPOINT ["./entrypoint.sh"]
