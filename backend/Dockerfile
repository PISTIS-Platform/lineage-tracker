# FROM --platform=linux/amd64 python:3.8-slim-buster as build
FROM python:3.8-slim-bullseye as build

# RUN apt-get update && apt-get install -y python3 python3-pip    

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /lineage-tracker/requirements.txt

WORKDIR /lineage-tracker
EXPOSE 8080

RUN pip install -r requirements.txt

COPY . .

WORKDIR /lineage-tracker/src 

ENTRYPOINT [ "python" ]

CMD [ "api.py" ]

