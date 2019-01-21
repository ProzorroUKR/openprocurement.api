FROM prozorro/base

COPY requirements.txt /app/

WORKDIR /app
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app
RUN pip install -e .

ENV PYTHONPATH "/app/src/openprocurement.api/src:${PYTHONPATH}"

EXPOSE 80

CMD ["chaussette", "--host", "0.0.0.0", "--port", "80", "--backend", "gevent", "paste:etc/service.ini"]
