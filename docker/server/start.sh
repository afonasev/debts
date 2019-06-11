#! /usr/bin/env sh
set -e

APP_MODULE="server.app:app"
BUILD_DEV=${BUILD_DEV}
HOST=0.0.0.0
WORKER_MAX_REQUESTS=${WORKER_MAX_REQUESTS:-50000}
WORKER_LIMIT_CONCURRENCY=${WORKER_LIMIT_CONCURRENCY:-1000}

if [ $BUILD_DEV == "true" ] ; then
    echo "[DEV BUILD]"
    exec uvicorn \
        --reload \
        --debug \
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
