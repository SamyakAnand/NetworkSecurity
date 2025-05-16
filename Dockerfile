FROM python:3.13-slim
WORKDIR /app
COPY . /app/

RUN apt update -y && apt install -r requirements.txt
CMD ["python3","app.py"]