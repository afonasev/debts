#! /usr/bin/env sh
set -e

APP_MODULE="server.app:app"
ENVIRONMENT=${ENVIRONMENT}
HOST=${HOST:-0.0.0.0}
MAX_REQUESTS=${MAX_REQUESTS}
LIMIT_CONCURRENCY=${LIMIT_CONCURRENCY}

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
        --limit-concurrency $LIMIT_CONCURRENCY \
        --limit-max-requests $MAX_REQUESTS \
        --no-access-log \
        --host $HOST \
        "$APP_MODULE"
fi
