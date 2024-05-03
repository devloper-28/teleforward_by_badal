FROM python:3.9-slim-buster

RUN mkdir ./app
RUN chmod 777 ./app
WORKDIR /app

RUN apt -qq update

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata

RUN apt -qq install -y  git
COPY requirements.txt .
COPY run.sh .

RUN pip3 install -r requirements.txt

CMD ["bash","run.sh"]
