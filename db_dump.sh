echo "Dump Database"
pg_dump --host=localhost --port=5432 --username=dbadmin --dbname=endogenous_supply_and_demand --file=database_dumps/endogenous_supply_and_demand.sql -v -Fc