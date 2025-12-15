FROM python:3.13-alpine3.20

RUN apk --no-cache add gcc build-base git openssl-dev libffi-dev

RUN addgroup -g 10000 user && \
    adduser -S -u 10000 -G user -h /app user

ENV APP_HOME=/app
WORKDIR ${APP_HOME}

RUN chown -R user:user ${APP_HOME}
USER user

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.4 /uv /uvx /bin/

ARG UV_EXTRA_ARGS="--no-dev"

# install deps
COPY pyproject.toml uv.lock ${APP_HOME}/
RUN uv sync --frozen --no-cache  ${UV_EXTRA_ARGS} --compile-bytecode

COPY ./ ${APP_HOME}/

# set the virtualenv
ENV VIRTUAL_ENV=${APP_HOME}/.venv
ENV PATH=${APP_HOME}/.venv/bin:$PATH
ENV PATH=${APP_HOME}:$PATH

ENV TZ=Europe/Kiev
ENV LANG="en_US.UTF-8"
ENV LC_ALL="en_US.UTF-8"
ENV LC_LANG="en_US.UTF-8"
ENV PYTHONIOENCODING="UTF-8"
ENV PYTHONPATH "/app/src/:${PYTHONPATH}"

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "-k", "gevent", "--paste", "/app/etc/service.ini", "--graceful-timeout=60", "--timeout=360"]
