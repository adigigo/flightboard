import os

PSQL_DB = os.getenv("PSQL_DB",'FlightRadar')
PSQL_USER = os.getenv("PSQL_USER", "adarsh")
PSQL_PASSWORD = os.getenv("PSQL_PASSWORD", "password123")
PSQL_PORT = os.getenv("PSQL_PORT", 5431)
PSQL_HOST = os.getenv("PSQL_HOST", "localhost")


LAT = os.getenv("LAT",35.879575)
LON = os.getenv("LON",-78.860621)
