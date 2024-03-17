FROM python:3.12-slim

COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip install -r requirements.txt
COPY . /opt/app

# RUN
CMD  ["python3", "src/data/make_dataset.py"]
