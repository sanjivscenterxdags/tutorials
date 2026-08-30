"""
Deliverable 2 — graphql_server.py

The entire GraphQL server for the tutorial, in one file.

    GraphQL operation      Resolver             SQL
    ---------------------  -------------------  --------------------------
    employees              get_employees()      SELECT
    employee(id)           get_employee()       SELECT ... WHERE
    addEmployee(...)       add_employee()       INSERT
    updateEmployee(...)    update_employee()    UPDATE
    deleteEmployee(id)     delete_employee()    DELETE

The architectural point of this tutorial is that the resolver functions below
talk *directly* to SQLite using the built-in `sqlite3` module. There is:

    - no ORM
    - no REST API layer
    - no repository / service / DAO class
    - no dependency injection

...so you can read one GraphQL operation all the way down to its SQL statement
without leaving this file.

Run it with:

    python graphql_server.py

Then open the GraphQL IDE at:

    http://localhost:8000/graphql
"""

import sqlite3
from pathlib import Path

import strawberry
import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route
from strawberry.asgi import GraphQL

# The same database file that create_database.py builds.
DB_FILE = Path(__file__).resolve().parent / "employees.db"

# Change this one constant if the port is busy on your machine. Port 8000 is a
# very common default (Docker containers, other tutorials), so we use 8008.
PORT = 8008


# ===========================================================================
# 1. THE GraphQL TYPE
# ===========================================================================
#
# This is the `type Employee { ... }` half of the GraphQL schema.
#
# We write the attributes in Python's snake_case; Strawberry exposes them to
# GraphQL clients in camelCase. That gives us the mapping the tutorial cares
# about:
#
#     SQLite column      Python attribute     GraphQL field
#     -------------      ----------------     -------------
#     employee_id   ->   employee_id     ->   employeeId
#     first_name    ->   first_name      ->   firstName
#     last_name     ->   last_name       ->   lastName
#     age           ->   age             ->   age
#     gender        ->   gender          ->   gender
#     position      ->   position        ->   position
#     salary        ->   salary          ->   salary
#     city          ->   city            ->   city


@strawberry.type
class Employee:
    employee_id: int
    first_name: str
    last_name: str
    age: int
    gender: str
    position: str
    salary: float
    city: str


def row_to_employee(row: tuple) -> Employee:
    """Convert one SQLite row tuple into an Employee GraphQL object.

    `SELECT * FROM Employee_Base_0` returns the columns in the order they were
    declared in the CREATE TABLE statement, so we can unpack positionally.
    This is step 4 of the resolver recipe described in each resolver below.
    """
    employee_id, first_name, last_name, age, gender, position, salary, city = row
    return Employee(
        employee_id=employee_id,
        first_name=first_name,
        last_name=last_name,
        age=age,
        gender=gender,
        position=position,
        salary=salary,
        city=city,
    )


# ===========================================================================
# 2. QUERY RESOLVERS  (GraphQL Query  ~  SQL SELECT)
# ===========================================================================
#
# Every resolver below performs the same six visible steps:
#
#     1. open a SQLite connection
#     2. execute a parameterized SQL statement
#     3. fetch the row or rows
#     4. convert the SQLite result to Employee object(s)
#     5. close the connection
#     6. return the result


@strawberry.type
class Query:
    @strawberry.field
    def employees(self) -> list[Employee]:
        """GraphQL:  query { employees { ... } }

                        |
                        v

        Resolver:   get_employees()

                        |
                        v

        SQL:        SELECT * FROM Employee_Base_0

        Note that the *client* decides which fields come back. This resolver
        always reads whole rows; GraphQL then trims the JSON response down to
        exactly the fields the query asked for. That is GraphQL field
        selection, and it is worth seeing in the IDE.
        """
        connection = sqlite3.connect(DB_FILE)          # 1. open
        cursor = connection.cursor()

        cursor.execute(                                 # 2. execute SQL
            "SELECT * FROM Employee_Base_0 ORDER BY employee_id"
        )

        rows = cursor.fetchall()                        # 3. fetch rows
        employees = [row_to_employee(row) for row in rows]   # 4. convert

        connection.close()                              # 5. close
        return employees                                # 6. return

    @strawberry.field
    def employee(self, id: int) -> Employee | None:
        """GraphQL:  query { employee(id: 5) { ... } }

                        |
                        v

        Resolver:   get_employee(5)

                        |
                        v

        SQL:        SELECT * FROM Employee_Base_0 WHERE employee_id = 5

        Returns null when no employee has that id — no exception, no custom
        error framework, just a GraphQL null.

        The `?` placeholder is required: client input is passed to SQLite as a
        *parameter*, never concatenated into the SQL text. (See §22 of the
        requirements — this is the SQL-injection lesson.)
        """
        connection = sqlite3.connect(DB_FILE)          # 1. open
        cursor = connection.cursor()

        cursor.execute(                                 # 2. execute SQL
            "SELECT * FROM Employee_Base_0 WHERE employee_id = ?",
            (id,),
        )

        row = cursor.fetchone()                         # 3. fetch row
        connection.close()                              # 5. close

        if row is None:
            return None

        return row_to_employee(row)                     # 4. convert / 6. return


# ===========================================================================
# 3. MUTATION RESOLVERS  (GraphQL Mutation  ~  SQL INSERT / UPDATE / DELETE)
# ===========================================================================


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_employee(
        self,
        first_name: str,
        last_name: str,
        age: int,
        gender: str,
        position: str,
        salary: float,
        city: str,
    ) -> Employee:
        """GraphQL:  mutation { addEmployee(firstName: "Alice", ...) { ... } }

                        |
                        v

        Resolver:   add_employee(...)

                        |
                        v

        SQL:        INSERT INTO Employee_Base_0 (...) VALUES (?, ?, ?, ?, ?, ?, ?)

        The client does *not* supply employeeId — SQLite generates it via
        AUTOINCREMENT. We read it back from cursor.lastrowid so the mutation
        can return the newly created employee, which is the normal GraphQL
        convention: a mutation returns the object it just changed.
        """
        connection = sqlite3.connect(DB_FILE)          # 1. open
        cursor = connection.cursor()

        cursor.execute(                                 # 2. execute SQL
            """
            INSERT INTO Employee_Base_0
                (first_name, last_name, age, gender, position, salary, city)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (first_name, last_name, age, gender, position, salary, city),
        )
        connection.commit()

        new_id = cursor.lastrowid                       # 3. the generated id
        connection.close()                              # 5. close

        # 4. return the new employee exactly as it now exists in the database
        return Employee(
            employee_id=new_id,
            first_name=first_name,
            last_name=last_name,
            age=age,
            gender=gender,
            position=position,
            salary=salary,
            city=city,
        )                                               # 6. return

    @strawberry.mutation
    def update_employee(
        self,
        employee_id: int,
        first_name: str,
        last_name: str,
        age: int,
        gender: str,
        position: str,
        salary: float,
        city: str,
    ) -> Employee | None:
        """GraphQL:  mutation { updateEmployee(employeeId: 3, ...) { ... } }

                        |
                        v

        Resolver:   update_employee(...)

                        |
                        v

        SQL:        UPDATE Employee_Base_0 SET ... WHERE employee_id = ?

        For an absolute-basics tutorial this is a *full-record* update: every
        field must be supplied. Partial-update semantics are a more advanced
        topic and are deliberately left out.

        Returns null when the employee_id does not exist. cursor.rowcount tells
        us how many rows the UPDATE actually touched.
        """
        connection = sqlite3.connect(DB_FILE)          # 1. open
        cursor = connection.cursor()

        cursor.execute(                                 # 2. execute SQL
            """
            UPDATE Employee_Base_0
            SET first_name = ?,
                last_name  = ?,
                age        = ?,
                gender     = ?,
                position   = ?,
                salary     = ?,
                city       = ?
            WHERE employee_id = ?
            """,
            (first_name, last_name, age, gender, position, salary, city, employee_id),
        )
        connection.commit()

        rows_changed = cursor.rowcount                  # 3. how many rows?
        connection.close()                              # 5. close

        if rows_changed == 0:
            return None                                 # no such employee

        # 4. return the updated employee
        return Employee(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            age=age,
            gender=gender,
            position=position,
            salary=salary,
            city=city,
        )                                               # 6. return

    @strawberry.mutation
    def delete_employee(self, employee_id: int) -> bool:
        """GraphQL:  mutation { deleteEmployee(employeeId: 10) }

                        |
                        v

        Resolver:   delete_employee(10)

                        |
                        v

        SQL:        DELETE FROM Employee_Base_0 WHERE employee_id = 10

        Returns a plain Boolean — true if a row was deleted, false if that id
        did not exist. The JSON response looks like:

            { "data": { "deleteEmployee": true } }

        Note that this mutation returns a scalar, not an object type, so the
        GraphQL operation has no selection set.
        """
        connection = sqlite3.connect(DB_FILE)          # 1. open
        cursor = connection.cursor()

        cursor.execute(                                 # 2. execute SQL
            "DELETE FROM Employee_Base_0 WHERE employee_id = ?",
            (employee_id,),
        )
        connection.commit()

        rows_deleted = cursor.rowcount                  # 3. how many rows?
        connection.close()                              # 5. close

        return rows_deleted > 0                         # 6. return


# ===========================================================================
# 4. THE SCHEMA AND THE /graphql ENDPOINT
# ===========================================================================
#
# The schema is the contract the client sees. Print it any time with:
#
#     python -c "from graphql_server import schema; print(schema)"

schema = strawberry.Schema(query=Query, mutation=Mutation)

# Strawberry's ASGI app. `graphql_ide="graphiql"` is the default and gives us
# the browser-based GraphQL IDE at the same URL.
graphql_app = GraphQL(schema, graphql_ide="graphiql")

# One endpoint, and only one: /graphql.
#
#   GET  /graphql  -> the browser GraphQL IDE (GraphiQL)
#   POST /graphql  -> every query and every mutation
#
# We use Route (an exact path match) rather than Mount, so that POST /graphql
# is answered directly instead of being redirected to /graphql/. That matters:
# the whole point of the curl exercises is that *every* operation is a plain
# POST to this one URL.
#
# CORS is wide open so that frontend/index.html can call this server when it is
# opened straight from disk (a file:// page sends `Origin: null`). That is fine
# for a local tutorial and is not a production setting.
app = Starlette(
    routes=[Route("/graphql", graphql_app, methods=["GET", "POST"])],
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
        )
    ],
)


if __name__ == "__main__":
    if not DB_FILE.exists():
        raise SystemExit(
            f"{DB_FILE} not found.\nRun `python create_database.py` first."
        )

    print(f"GraphQL IDE:  http://localhost:{PORT}/graphql")
    print(f"Endpoint:     POST http://localhost:{PORT}/graphql")
    uvicorn.run(app, host="127.0.0.1", port=PORT)
