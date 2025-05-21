FROM python:3.11-alpine3.20

RUN apk --no-cache add gcc build-base git openssl-dev libffi-dev

RUN addgroup -g 10000 user && \
    adduser -S -u 10000 -G user -h /app user

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# TODO: Remove for production build
COPY requirements-test.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements-test.txt

COPY . /app
RUN pip install -e .

RUN chown -R user:user /app
USER user

ENV TZ=Europe/Kiev
ENV LANG="en_US.UTF-8"
ENV LC_ALL="en_US.UTF-8"
ENV LC_LANG="en_US.UTF-8"
ENV PYTHONIOENCODING="UTF-8"
ENV PYTHONPATH "/app/src/:${PYTHONPATH}"

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "-k", "gevent", "--paste", "/app/etc/service.ini", "--graceful-timeout=60", "--timeout=360"]
