# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install python-telegram-bot --upgrade

COPY . .

CMD [ "python3", "run.py", "-m"]
