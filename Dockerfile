FROM tiangolo/uvicorn-gunicorn:python3.11-slim

LABEL maintainer="Joonyeonglim <lyt970120@gmail.com>"

COPY requirements.txt /tmp/requirements.txt
RUN apt-get update && apt-get upgrade -y && apt-get install gcc g++ -y
RUN pip install --upgrade pip && pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN pip install --no-cache-dir pexpect
COPY ./app /app
EXPOSE 80
