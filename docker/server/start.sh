#! /usr/bin/env sh
set -e

APP_MODULE="server.app:app"
ENVIRONMENT=${ENVIRONMENT}
HOST=${HOST:-0.0.0.0}
WORKER_MAX_REQUESTS=${WORKER_MAX_REQUESTS}
WORKER_LIMIT_CONCURRENCY=${WORKER_LIMIT_CONCURRENCY}

echo "ENVIRONMENT: ${ENVIRONMENT}"

if [ $ENVIRONMENT == "dev" ] ; then
    exec uvicorn \
        --reload \
        --debug \
        --no-access-log \
        --host $HOST \
        "$APP_MODULE"
else
    exec uvicorn \
        --limit-concurrency $WORKER_LIMIT_CONCURRENCY \
        --limit-max-requests $WORKER_MAX_REQUESTS \
        --no-access-log \
        --host $HOST \
        "$APP_MODULE"
fi
