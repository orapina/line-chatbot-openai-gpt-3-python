FROM python:3.10-alpine

# Install dependencies
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    libc-dev \
    linux-headers \
    musl-dev \
    postgresql-dev \
    && apk add --no-cache \
    bash \
    postgresql-client \
    && pip install --upgrade pip

# Install pip dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY . /app
WORKDIR /app

# Run server
CMD ["python", "line_webhook.py"]