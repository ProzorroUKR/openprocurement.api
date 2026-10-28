# glibc-based image: musl's allocator is slow for allocation-heavy Python workloads
# base images are pinned by digest, so every build gets exactly the same image;
# to update, bump the tag and the digest together
ARG PYTHON_IMAGE=python:3.13-slim-trixie@sha256:b3575dcf816cdacc5292df77a6e3e59b8941631078373a045efa2ac1e9c5c3b2
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.11.33@sha256:77280f2f771df71f90786c314fe1bbc1e023feac652969bbf139c280babf2eb7

FROM ${UV_IMAGE} AS uv


# build stage: compilers, git and -dev headers are needed only to build the virtualenv
FROM ${PYTHON_IMAGE} AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential git libssl-dev libffi-dev && \
    rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /uvx /bin/

ARG UV_EXTRA_ARGS="--no-dev"

# the virtualenv is built at the same path it is used at in the runtime stage
WORKDIR /app
COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --no-cache  ${UV_EXTRA_ARGS} --compile-bytecode


# runtime stage
FROM ${PYTHON_IMAGE}

# tzdata-legacy: Debian 13 moved old zone names like Europe/Kiev (see TZ below) there,
# without it the system local time silently falls back to UTC.
# pip is removed: the app runs from the uv virtualenv, and pip ships its own outdated urllib3 copy.
# setuid/setgid bits are stripped (su, mount, passwd, ...): nothing here needs them,
# and they are a way to gain root from inside the container
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata-legacy && \
    rm -rf /var/lib/apt/lists/* && \
    python -m pip uninstall -y pip && \
    find / -xdev -perm /6000 -type f -exec chmod a-s {} +

# the app user owns nothing in /app (no home dir is created there):
# the code and the virtualenv stay root-owned and read-only for the running process
RUN groupadd -g 10000 user && \
    useradd -r -u 10000 -g user -d /app -M user

ENV APP_HOME=/app
WORKDIR ${APP_HOME}

# uv stays in the runtime image: CI runs the tests inside it with `uv run`
COPY --from=uv /uv /uvx /bin/

COPY --from=builder /app/.venv ${APP_HOME}/.venv

COPY ./ ${APP_HOME}/

# numeric uid:gid, so Kubernetes runAsNonRoot can verify the user is not root
USER 10000:10000

# set the virtualenv
ENV VIRTUAL_ENV=${APP_HOME}/.venv
ENV PATH=${APP_HOME}/.venv/bin:$PATH
# the home dir (/app) is read-only, so uv keeps its cache in /tmp
ENV UV_CACHE_DIR=/tmp/uv-cache

ENV TZ=Europe/Kiev
ENV LANG="en_US.UTF-8"
ENV LC_ALL="en_US.UTF-8"
ENV LC_LANG="en_US.UTF-8"
ENV PYTHONIOENCODING="UTF-8"
# no trailing ":" here: an empty entry would put the current directory on sys.path
ENV PYTHONPATH=/app/src

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "-k", "gevent", "--paste", "/app/etc/service.ini", "--graceful-timeout=60", "--timeout=360"]
