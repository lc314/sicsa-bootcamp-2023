FROM python:latest

WORKDIR /app

RUN apt update && apt -y upgrade

# Install Python requirements
ENV PIP_NO_CACHE_DIR=1
RUN python3 -m pip install --upgrade pip
COPY ./app/requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt

# Copy application code
COPY ./app .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "1234", "--proxy-headers"]
