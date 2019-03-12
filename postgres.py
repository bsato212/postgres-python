from os import getenv
from flask import jsonify

from psycopg2 import OperationalError
from psycopg2.pool import SimpleConnectionPool

CONNECTION_NAME = getenv('INSTANCE_CONNECTION_NAME')
DB_USER = getenv('DB_USER')
DB_PASSWORD = getenv('DB_PASSWORD')
DB_NAME = getenv('DB_NAME')

pg_config = {
  'user': DB_USER,
  'password': DB_PASSWORD,
  'dbname': DB_NAME
}

# Connection pools reuse connections between invocations,
# and handle dropped or expired connections automatically.
pg_pool = None


def __connect(host):
    """
    Helper function to connect to Postgres
    """
    global pg_pool
    pg_config['host'] = host
    pg_pool = SimpleConnectionPool(1, 10, **pg_config)


def postgres(request):
    global pg_pool

    # Initialize the pool lazily, in case SQL access isn't needed for this
    # GCF instance. Doing so minimizes the number of active SQL connections,
    # which helps keep your GCF instances under SQL connection limits.
    if not pg_pool:
        try:
            __connect(f'/cloudsql/{CONNECTION_NAME}')
        except OperationalError:
            # If production settings fail, use local development ones
            __connect('localhost')

    # Remember to close SQL resources declared while running this function.
    # Keep any declared in global scope (e.g. pg_pool) for later reuse.
    with pg_pool.getconn().cursor() as cursor:
        cursor.execute('SELECT * FROM rover_exclude')
        results = cursor.fetchall()
        return jsonify(results)
