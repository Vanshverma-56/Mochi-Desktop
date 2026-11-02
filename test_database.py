
from mochi.database.connection import Database
from mochi.database.schema import initialise_database

db = Database()

initialise_database(db)

print("\nDatabase:", db.database_path)

tables = db.connect().execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
)

print("\nTables created:")

for table in tables:
    print("-", table["name"])

db.close()

print("\nDatabase verification completed.")
