FROM python:3.11-slim AS builder
ARG APP_DIR=/main/app

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  PATH="/root/.local/bin:$PATH" \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get -y upgrade && apt-get install -y curl

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR ${APP_DIR}

COPY bin ./bin/
COPY vulnerabilitylookup ./vulnerabilitylookup/

COPY mypy.ini poetry.lock pyproject.toml README.md ./

RUN poetry install --no-interaction --no-ansi

FROM python:3.11-slim
ARG APP_DIR=/main/app

ARG STORAGE_HOSTNAME
ARG STORAGE_PORT

ARG CSAF_PATH=/opt/csaf
ARG CSAF_VERSION=3.2.0
ARG INSTANCE_NAME
ARG INSTANCE_UUID
ARG POSTGRES_HOSTNAME
ARG POSTGRES_DATABASE
ARG POSTGRES_PASSWORD

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  PATH="/root/.local/bin:$PATH"

RUN apt-get update && apt-get -y upgrade && apt-get install -y curl git libtool libssl-dev

WORKDIR ${APP_DIR}

# Install Vulnerability Lookup
COPY bin ./bin/
COPY cache ./cache/
COPY config ./config/
COPY etc ./etc/
COPY storage ./storage/
COPY tests ./tests/
COPY tools ./tools/
COPY vulnerabilitylookup ./vulnerabilitylookup/
COPY website ./website/

COPY .git ./.git/

RUN mkdir -p ./logs && echo VULNERABILITYLOOKUP_HOME="${APP_DIR}" >> .env

RUN mv ${APP_DIR}/config/generic.json.sample ${APP_DIR}/config/generic.json && \
    mv ${APP_DIR}/config/logging.json.sample ${APP_DIR}/config/logging.json && \
    mv ${APP_DIR}/config/modules.cfg.sample ${APP_DIR}/config/modules.cfg && \
    mv ${APP_DIR}/config/stream.json.sample ${APP_DIR}/config/stream.json && \
    mv ${APP_DIR}/config/website.py.sample ${APP_DIR}/config/website.py && \
    git config --global pull.ff only

RUN sed -i 's@\("storage_db_hostname": *"\)[^"]*@\1'"$STORAGE_HOSTNAME"'@' ${APP_DIR}/config/generic.json && \
    sed -i 's@\("storage_db_port": *"\)[^"]*@\1'"$STORAGE_PORT"'@' ${APP_DIR}/config/generic.json && \
    sed -i 's@\("public_domain": *"\)[^"]*@\1'"127.0.0.1:10001"'@' ${APP_DIR}/config/generic.json && \
    sed -i 's@\("csaf_downloader_path": *"\)[^"]*@\1'"$CSAF_PATH/bin-linux-amd64/csaf_downloader"'@' ${APP_DIR}/config/generic.json && \
    sed -i 's@\("local_instance_name": *"\)[^"]*@\1'"$INSTANCE_NAME"'@' ${APP_DIR}/config/generic.json && \
    sed -i 's@\("local_instance_uuid": *"\)[^"]*@\1'"$INSTANCE_UUID"'@' ${APP_DIR}/config/generic.json && \
    sed -i "/\"host\": *\"127\.0\.0\.1\"/s/\"127\.0\.0\.1\"/\"${POSTGRES_HOSTNAME}\"/" ${APP_DIR}/config/website.py && \
    sed -i "/DATABASE_NAME = \"vulnlookup\"/s/\"vulnlookup\"/\"${POSTGRES_DATABASE}\"/" ${APP_DIR}/config/website.py && \
    sed -i "/\"password\": *\"password\"/s/\"password\",/\"${POSTGRES_PASSWORD}\",/" ${APP_DIR}/config/website.py

EXPOSE 10001

# Copy dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

CMD ["gunicorn", "-w", "1", "--worker-class", "gevent", "--graceful-timeout", "2",\
    "--timeout", "300","-b", "0.0.0.0:10001","--log-level", "info", "--reuse-port", "website.app"]
