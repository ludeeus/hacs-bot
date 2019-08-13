FROM python:3.7

ENV PYTHONUNBUFFERED=0

COPY requirements.txt /app/requirements.txt
COPY bot /app

RUN pip3 install -r /app/requirements.txt

ENTRYPOINT ["python3", "-u", "/app"]