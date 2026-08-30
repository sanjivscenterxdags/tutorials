"""
Deliverable 1 — create_database.py

Creates the SQLite database used by the GraphQL tutorial.

    employees.db
        └── Employee_Base_0   (10 sample rows)

This script is deliberately repeatable: it DROPs and recreates the table every
time it runs, so you can always get back to a known-good starting point.

Run it with:

    python create_database.py

Nothing in this file knows anything about GraphQL. It is plain Python + the
built-in `sqlite3` module. That separation is intentional: the GraphQL layer
added in graphql_server.py sits directly on top of *this* database, with no
ORM and no REST API in between.
"""

import sqlite3
from pathlib import Path

# The database file lives next to this script, so it does not matter which
# directory you run the script from. graphql_server.py resolves it the same way.
DB_FILE = Path(__file__).resolve().parent / "employees.db"


# ---------------------------------------------------------------------------
# 1. Table definition
# ---------------------------------------------------------------------------
#
# SQLite column      ->   GraphQL field   (see graphql_server.py)
#
#   employee_id      ->   employeeId
#   first_name       ->   firstName
#   last_name        ->   lastName
#   age              ->   age
#   gender           ->   gender
#   position         ->   position
#   salary           ->   salary
#   city             ->   city
#
# SQLite uses snake_case. GraphQL conventionally uses camelCase. Strawberry
# performs that conversion for us — but the mapping is worth keeping in view.

CREATE_TABLE_SQL = """
CREATE TABLE Employee_Base_0 (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name  TEXT    NOT NULL,
    last_name   TEXT    NOT NULL,
    age         INTEGER NOT NULL,
    gender      TEXT    NOT NULL,
    position    TEXT    NOT NULL,
    salary      REAL    NOT NULL,
    city        TEXT    NOT NULL
)
"""


# ---------------------------------------------------------------------------
# 2. Sample data — exactly ten employees
# ---------------------------------------------------------------------------

SAMPLE_EMPLOYEES = [
    # (first_name, last_name, age, gender, position,          salary,    city)
    ("John",     "Smith",    38, "Male",   "Engineer",         95000.00, "Dallas"),
    ("Mary",     "Jones",    42, "Female", "Manager",         125000.00, "Chicago"),
    ("Robert",   "Brown",    29, "Male",   "Analyst",          72000.00, "Boston"),
    ("Linda",    "Wilson",   35, "Female", "Developer",        98000.00, "Austin"),
    ("David",    "Miller",   46, "Male",   "Architect",       145000.00, "Denver"),
    ("Susan",    "Davis",    31, "Female", "Consultant",       88000.00, "Atlanta"),
    ("James",    "Anderson", 40, "Male",   "Project Manager", 118000.00, "Seattle"),
    ("Karen",    "Thomas",   27, "Female", "Engineer",         84000.00, "Phoenix"),
    ("Michael",  "Jackson",  51, "Male",   "Director",        165000.00, "New York"),
    ("Patricia", "Martin",   37, "Female", "Product Manager", 110000.00, "Miami"),
]

INSERT_SQL = """
INSERT INTO Employee_Base_0
    (first_name, last_name, age, gender, position, salary, city)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""


def main() -> None:
    print(f"Database file: {DB_FILE}")

    # 1. open a connection (creates the file if it does not exist yet)
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    # 2. start from a clean slate so the script can be run over and over
    cursor.execute("DROP TABLE IF EXISTS Employee_Base_0")
    print("Dropped Employee_Base_0 (if it existed).")

    # 3. create the table
    cursor.execute(CREATE_TABLE_SQL)
    print("Created table Employee_Base_0.")

    # 4. insert the ten sample rows.
    #    Note the `?` placeholders — values are never glued into the SQL string.
    cursor.executemany(INSERT_SQL, SAMPLE_EMPLOYEES)
    connection.commit()
    print(f"Inserted {len(SAMPLE_EMPLOYEES)} employees.")

    # 5. verify — read the rows straight back out
    print("\nVerification — SELECT * FROM Employee_Base_0;\n")
    header = f"{'id':>3}  {'first':<9} {'last':<9} {'age':>3}  {'gender':<7} {'position':<16} {'salary':>10}  city"
    print(header)
    print("-" * len(header))

    for row in cursor.execute("SELECT * FROM Employee_Base_0 ORDER BY employee_id"):
        employee_id, first, last, age, gender, position, salary, city = row
        print(
            f"{employee_id:>3}  {first:<9} {last:<9} {age:>3}  "
            f"{gender:<7} {position:<16} {salary:>10.2f}  {city}"
        )

    # 6. close the connection
    connection.close()
    print("\nDone. Next step: python graphql_server.py")


if __name__ == "__main__":
    main()
