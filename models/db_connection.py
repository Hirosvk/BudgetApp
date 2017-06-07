import psycopg2 
import os

dbname = os.getenv('BUDGET_APP_DBNAME')
username = os.getenv('BUDGET_APP_USERNAME')
password = os.getenv('BUDGET_APP_PASSWORD')
hostname = os.getenv('BUDGET_APP_HOSTNAME')
port = os.getenv('BUDGET_APP_PORT')

db_settings = "dbname='" + dbname + "'"
if username:
    db_settings += "user='" + username + "'"

if password:
    db_settings += "password='" + password + "'"

if hostname:
    db_settings += "host='" + hostname + "'"

if port:
    db_settings += "port=" + port

conn = psycopg2.connect(db_settings)
conn.autocommit = True
# without this flag set to True, Postgres server throws errors with 'unexpected EOF on client' Below is an exerpt from python documentation.

#   autocommit
    #   Read/write attribute: if True, no transaction is handled by the driver and every statement sent to the backend has immediate effect; if False a new transaction is started at the first command execution: the methods commit() or rollback() must be manually invoked to terminate the transaction.

    #   The autocommit mode is useful to execute commands requiring to be run outside a transaction, such as CREATE DATABASE or VACUUM.

    #   The default is False (manual commit) as per DBAPI specification.

    #   Warning By default, any query execution, including a simple SELECT will start a transaction: for long-running programs, if no further action is taken, the session will remain "idle in transaction", an undesirable condition for several reasons (locks are held by the session, tables bloat...). For long lived scripts, either ensure to terminate a transaction as soon as possible or use an autocommit connection.

DB = conn.cursor()

