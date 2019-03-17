FROM python:2.7-jessie

COPY requirements.txt /app/
RUN pip install -r requirements.txt

WORKDIR /app
COPY . /app
RUN pip install --upgrade pip && pip install -e .

ENV PYTHONPATH "/app/src:${PYTHONPATH}"

EXPOSE 80

CMD ["chaussette", "--host", "0.0.0.0", "--port", "80", "--backend", "gevent", "paste:etc/service.ini"]
