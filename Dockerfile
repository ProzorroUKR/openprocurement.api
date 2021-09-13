# Dockerfile is not optimized, for optimized build use werf.yml
FROM python:3.8-slim

RUN apt-get update && apt-get install -y git gcc libssl-dev

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt

COPY . /app
RUN pip install -e .

ENV TZ=Europe/Kiev
ENV LANG="en_US.UTF-8"
ENV LC_ALL="en_US.UTF-8"
ENV LC_LANG="en_US.UTF-8"
ENV PYTHONIOENCODING="UTF-8"
ENV PYTHONPATH "/app/src/:${PYTHONPATH}"

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "-k", "gevent", "--paste", "/app/etc/service.ini", "--graceful-timeout=60", "--timeout=360"]
