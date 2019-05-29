#!/bin/bash
set -e

function db_ready(){
python << END
import sys
import sqlalchemy

try:
    engine_pro = sqlalchemy.create_engine("${DATABASE}").connect()
except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
    print('Error:', e)
    sys.exit(-1)
sys.exit(0)
END
}

until db_ready; do
  >&2 echo 'Waiting for database to become available...'
  sleep 1
done

exec "$@"
