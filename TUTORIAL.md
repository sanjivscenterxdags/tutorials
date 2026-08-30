# GraphQL Absolute Basics — Type-It-Yourself Tutorial

**You will type every line of this yourself.** That is the point. Reading
finished code teaches you what it looks like; typing it, running it, and
breaking it teaches you how it *works*.

By the end you will have built, from an empty directory:

- a SQLite database
- a GraphQL server whose resolvers run SQL you can watch scroll past
- `curl` commands that drive it
- a browser page using Apollo Client

**Time:** about 3 hours. **Prerequisite:** you can run `python`.

---

## How this tutorial works

Every step follows the same rhythm:

| | |
|---|---|
| **Type** | Code to type. Type it — don't copy-paste. Typos are part of the lesson. |
| **Run** | The exact command. |
| **You should see** | Expected output. If yours differs, stop and reconcile. |
| **What just happened** | The concept you just made real. |
| **Break it** | A deliberate mistake. Do these — they are the most valuable minutes here. |

### Your workspace

You will build everything in a **`tutorial/`** directory. The finished
reference versions live in the project root (`create_database.py`,
`graphql_server.py`, `frontend/index.html`) — treat those as the answer key.
Peek only after you have tried.

Your server will run on **port 8009**; the reference one uses 8008, so both can
run at once without colliding.

### Set up

```bash
cd /Users/sanjivsingh/pydev16/max002/trng/gqL
mkdir -p tutorial
```

Check your tools:

```bash
uv run python -c "import strawberry, uvicorn; print('dependencies OK')"
```

If that errors, run `uv sync` first.

### You will want two terminals

- **Terminal A** — runs the server. You will *watch* this one.
- **Terminal B** — runs `curl` and scripts.

---

# Phase 1 — The Database

**~15 minutes.** No GraphQL yet. First, data to serve.

## Step 1.1 — Create a table and one row

**Type** — `tutorial/create_database.py`:

```python
import sqlite3
from pathlib import Path

# Put the database next to this script, so it doesn't matter which
# directory you run the script from.
DB_FILE = Path(__file__).resolve().parent / "employees.db"

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()

cursor.execute("""
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
""")

cursor.execute(
    """
    INSERT INTO Employee_Base_0
        (first_name, last_name, age, gender, position, salary, city)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    ("John", "Smith", 38, "Male", "Engineer", 95000.00, "Dallas"),
)

connection.commit()

for row in cursor.execute("SELECT * FROM Employee_Base_0"):
    print(row)

connection.close()
```

**Run:**

```bash
uv run python tutorial/create_database.py
```

**You should see:**

```text
(1, 'John', 'Smith', 38, 'Male', 'Engineer', 95000.0, 'Dallas')
```

**What just happened**

You never supplied `employee_id` — SQLite generated the `1` because the column
is `INTEGER PRIMARY KEY AUTOINCREMENT`. Remember this; in Phase 4 the
`addEmployee` mutation relies on exactly this behaviour.

Note the `?` placeholders. The values travel to SQLite *separately* from the
SQL text. We will come back to why that matters.

---

## Step 1.2 — Break it: run it twice

**Run** the same command again:

```bash
uv run python tutorial/create_database.py
```

**You should see:**

```text
sqlite3.OperationalError: table Employee_Base_0 already exists
```

**What just happened**

The script isn't repeatable, and a tutorial script you can't re-run is useless
— you need a reset button.

**Fix it.** Add this line immediately *before* the `CREATE TABLE`:

```python
cursor.execute("DROP TABLE IF EXISTS Employee_Base_0")
```

Run it twice more. It now works every time, and always prints exactly one row.

> From here on, `uv run python tutorial/create_database.py` is your **reset
> button**. Any time your data gets into a confusing state, run it.

---

## Step 1.3 — Ten rows

**Type** — replace the single `cursor.execute(INSERT ...)` call with a list and
one `executemany`:

```python
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

cursor.executemany(
    """
    INSERT INTO Employee_Base_0
        (first_name, last_name, age, gender, position, salary, city)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    SAMPLE_EMPLOYEES,
)
```

**Run** it, and you should see ten tuples with ids 1 through 10.

**Optional** — look at the database with the `sqlite3` command-line tool:

```bash
sqlite3 tutorial/employees.db "SELECT employee_id, first_name, city FROM Employee_Base_0 LIMIT 3;"
```

**Phase 1 done.** You have a database. Nothing so far is GraphQL-specific —
that is deliberate. GraphQL sits *on top of* ordinary data.

---

# Phase 2 — The Smallest Possible GraphQL Server

**~20 minutes.** We will not touch SQLite in this phase. First understand what
a GraphQL server *is*, with nothing else in the way.

## Step 2.1 — Hello, schema

**Type** — `tutorial/server.py`, complete file:

```python
import strawberry
import uvicorn
from strawberry.asgi import GraphQL


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from GraphQL"


schema = strawberry.Schema(query=Query)
app = GraphQL(schema)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8009)
```

**Run** — in **Terminal A**, and leave it running:

```bash
uv run python tutorial/server.py
```

**You should see:**

```text
INFO:     Uvicorn running on http://127.0.0.1:8009 (Press CTRL+C to quit)
```

**Try it.** Open <http://localhost:8009/> in a browser. You get **GraphiQL**,
the built-in GraphQL IDE. Type this on the left and press the ▶ button:

```graphql
query {
  hello
}
```

```json
{ "data": { "hello": "Hello from GraphQL" } }
```

**What just happened**

Four ideas, all present in fifteen lines:

1. **Schema** — `strawberry.Schema(query=Query)`. The contract: everything a
   client is allowed to ask for.
2. **Query type** — the entry point for reads.
3. **Field** — `hello`, with a declared type `str` → GraphQL `String!`.
4. **Resolver** — the Python function *behind* the field. GraphQL calls it to
   produce the value. Right now it returns a constant; soon it will run SQL.

The response key `"hello"` is the field name. The `"data"` envelope is standard
GraphQL: results under `data`, problems under `errors`.

**Explore.** In GraphiQL, click **Docs** (top left). Browse the schema
Strawberry generated from your Python types. You never wrote a schema file —
your type annotations *are* the schema.

---

## Step 2.2 — An object type, still hardcoded

A `String` field is not interesting. Real GraphQL is about **object types**.

**Type** — add above `Query`, and replace `Query` entirely:

```python
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


@strawberry.type
class Query:
    @strawberry.field
    def employee(self) -> Employee:
        return Employee(
            employee_id=1,
            first_name="John",
            last_name="Smith",
            age=38,
            gender="Male",
            position="Engineer",
            salary=95000.00,
            city="Dallas",
        )
```

> **Note the keyword arguments.** Strawberry types do *not* accept positional
> arguments — `Employee(1, "John", ...)` raises `TypeError`. Always name them.

**Run** — stop Terminal A with `Ctrl+C` and start it again. (Do this after
every server edit. There is no auto-reload here.)

**Try it** in GraphiQL:

```graphql
query {
  employee {
    firstName
    city
  }
}
```

```json
{ "data": { "employee": { "firstName": "John", "city": "Dallas" } } }
```

**What just happened — this is the big one**

You wrote `first_name` in Python. You asked for `firstName` in GraphQL.
Strawberry converts snake_case to camelCase automatically:

```text
Python / SQLite          GraphQL
employee_id        ->    employeeId
first_name         ->    firstName
last_name          ->    lastName
```

Second, and more important: **you asked for two fields and got exactly two
fields.** The resolver built a whole `Employee` with eight fields. GraphQL
trimmed the response to what you selected. That is **field selection**, and it
is the single biggest difference from REST — the *client* decides the shape of
the response, not the server.

**Try it:** add `salary` and `position` to your selection and re-run. The
resolver did not change. The response did.

---

## Step 2.3 — Break it: three schema errors

Run each of these in GraphiQL. Read the error; they are unusually good.

**(a) Use the Python name instead of the GraphQL name:**

```graphql
query { employee { employee_id } }
```

```text
Cannot query field 'employee_id' on type 'Employee'. Did you mean 'employeeId'?
```

The error teaches you the mapping.

**(b) Ask for a field that doesn't exist:**

```graphql
query { employee { salaryUsd } }
```

```text
Cannot query field 'salaryUsd' on type 'Employee'. Did you mean 'salary'?
```

**(c) Break the syntax — delete a closing brace:**

```graphql
query { employee { firstName
```

```text
Syntax Error: Expected Name, found <EOF>.
```

**What just happened**

You did not write any of that error handling. The schema is a **contract**, and
GraphQL enforces it *before* your resolver ever runs. In Phase 3 you will see
proof of that, with your own eyes.

---

# Phase 3 — Real Resolvers: GraphQL Meets SQL

**~30 minutes.** Now connect the schema to the database.

## Step 3.1 — `employees` → `SELECT`

**Type** — add these imports at the top of `tutorial/server.py`:

```python
import sqlite3
from pathlib import Path
```

and below the imports:

```python
DB_FILE = Path(__file__).resolve().parent / "employees.db"
```

Now **replace** the hardcoded `employee` field with a real one. Replace your
whole `Query` class with:

```python
@strawberry.type
class Query:
    @strawberry.field
    def employees(self) -> list[Employee]:
        # 1. open a connection
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        # 2. execute SQL  -- printed so you can watch it in Terminal A
        sql = "SELECT * FROM Employee_Base_0 ORDER BY employee_id"
        print(f"\n  RESOLVER  employees()")
        print(f"  SQL       {sql}")

        cursor.execute(sql)

        # 3. fetch the rows
        rows = cursor.fetchall()
        print(f"  ROWS      {len(rows)} returned")

        # 4. convert each row into an Employee object
        result = []
        for row in rows:
            result.append(
                Employee(
                    employee_id=row[0],
                    first_name=row[1],
                    last_name=row[2],
                    age=row[3],
                    gender=row[4],
                    position=row[5],
                    salary=row[6],
                    city=row[7],
                )
            )

        # 5. close the connection
        connection.close()

        # 6. return
        return result
```

**Run** — restart Terminal A. In GraphiQL:

```graphql
query {
  employees {
    employeeId
    firstName
    lastName
    position
    city
  }
}
```

You get ten employees. **Now look at Terminal A:**

```text
  RESOLVER  employees()
  SQL       SELECT * FROM Employee_Base_0 ORDER BY employee_id
  ROWS      10 returned
```

**What just happened**

That is the whole architecture, and you just watched it happen live:

```text
GraphQL query   ->   resolver function   ->   SQL   ->   SQLite rows
                                                              |
                     JSON response   <-   Employee objects  <-+
```

No ORM. No REST endpoint in between. A GraphQL field, a Python function, and a
SQL string you can read.

Keep Terminal A visible for the rest of the tutorial.

**Try it:** run the query again asking only for `firstName`. The SQL in
Terminal A is *unchanged* — still `SELECT *`, still 10 rows. Only the JSON
shrank. Field selection happens **after** the resolver, in GraphQL's response
layer.

---

## Step 3.2 — Break it: watch validation happen before SQL

In GraphiQL, run a query with a bad field name:

```graphql
query { employees { employee_id } }
```

You get the "Did you mean 'employeeId'?" error. **Now look at Terminal A.**

**Nothing was printed.** No resolver ran. No SQL executed. No connection was
opened.

**What just happened**

GraphQL validated your query against the schema and rejected it *before*
execution. An invalid query never reaches your database. This is what people
mean when they call a GraphQL schema a contract — it is checked, not merely
documented.

---

## Step 3.3 — `employee(id)` → arguments and parameterized SQL

**Type** — add a second field inside `Query`, below `employees`:

```python
    @strawberry.field
    def employee(self, id: int) -> Employee | None:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        sql = "SELECT * FROM Employee_Base_0 WHERE employee_id = ?"
        print(f"\n  RESOLVER  employee({id})")
        print(f"  SQL       {sql}   params=({id},)")

        cursor.execute(sql, (id,))

        row = cursor.fetchone()
        print(f"  ROW       {row}")
        connection.close()

        if row is None:
            return None

        return Employee(
            employee_id=row[0],
            first_name=row[1],
            last_name=row[2],
            age=row[3],
            gender=row[4],
            position=row[5],
            salary=row[6],
            city=row[7],
        )
```

**Run** — restart, then in GraphiQL:

```graphql
query {
  employee(id: 5) {
    employeeId
    firstName
    lastName
    position
    salary
    city
  }
}
```

```json
{ "data": { "employee": { "employeeId": 5, "firstName": "David", ... } } }
```

**What just happened**

Three new ideas:

**Arguments.** The Python parameter `id: int` became the GraphQL argument
`employee(id: Int!)`. The `!` means required — check it in the Docs panel.

**Nullable return.** `-> Employee | None` became `Employee` (no `!`) in GraphQL.
Try `id: 999`:

```json
{ "data": { "employee": null } }
```

Terminal A shows the SQL *did* run and returned `ROW None`. A missing row is
not an error — it is a `null`. That is the normal GraphQL way to say "no such
thing."

**Parameterized SQL.** This is the one habit to take away from this tutorial:

```python
cursor.execute(sql, (id,))          # value passed separately  ✅
```

Never this:

```python
cursor.execute("... WHERE employee_id = " + str(id))   # ❌ SQL injection
```

With `?`, SQLite treats the value strictly as *data* — it can never be parsed
as SQL. Concatenation lets a caller smuggle in SQL of their own. Every resolver
you write from here uses `?`.

---

## Step 3.4 — Variables

So far you have typed literal values *inside* the query. Real clients send
**variables** instead.

**Try it** in GraphiQL. Query pane:

```graphql
query GetEmployee($id: Int!) {
  employee(id: $id) {
    employeeId
    firstName
    lastName
    position
  }
}
```

**Variables** pane (bottom-left panel — open it if collapsed):

```json
{ "id": 5 }
```

Same result. Change the variable to `3` and re-run without touching the query.

**What just happened**

The query text is now a fixed, reusable template; only the data changes. Two
new pieces of syntax:

- `query GetEmployee(...)` — an *operation name* and its variable declarations
- `$id: Int!` — declares a variable, which must match the argument's type

This is how every real client works, including the Apollo page you build in
Phase 6.

**Phase 3 done.** Reads work. Now writes.

---

# Phase 4 — Mutations

**~40 minutes.** In GraphQL, anything that changes data is a **mutation**.
Queries read; mutations write. The distinction is a convention GraphQL enforces
structurally — they live in different root types.

## Step 4.1 — `addEmployee` → `INSERT`

**Type** — add a new class at the bottom of `tutorial/server.py`, *above* the
`schema = ...` line:

```python
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
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        sql = """
            INSERT INTO Employee_Base_0
                (first_name, last_name, age, gender, position, salary, city)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        print(f"\n  RESOLVER  add_employee({first_name!r}, {last_name!r}, ...)")
        print(f"  SQL       INSERT INTO Employee_Base_0 ...")

        cursor.execute(
            sql,
            (first_name, last_name, age, gender, position, salary, city),
        )
        connection.commit()

        new_id = cursor.lastrowid
        print(f"  NEW ID    {new_id}   (generated by SQLite)")
        connection.close()

        return Employee(
            employee_id=new_id,
            first_name=first_name,
            last_name=last_name,
            age=age,
            gender=gender,
            position=position,
            salary=salary,
            city=city,
        )
```

**Type** — now update the schema line to register mutations:

```python
schema = strawberry.Schema(query=Query, mutation=Mutation)
```

**Run** — restart. In GraphiQL:

```graphql
mutation {
  addEmployee(
    firstName: "Alice"
    lastName: "Cooper"
    age: 34
    gender: "Female"
    position: "Engineer"
    salary: 102000.00
    city: "Houston"
  ) {
    employeeId
    firstName
    lastName
    position
  }
}
```

```json
{ "data": { "addEmployee": { "employeeId": 11, "firstName": "Alice", ... } } }
```

**What just happened**

- The operation starts with `mutation`, not `query`.
- You sent seven arguments and no `employeeId` — SQLite generated `11`.
- `cursor.lastrowid` gave you that generated id, so the mutation could return
  the row it created. **Mutations returning the changed object is the GraphQL
  convention** — it saves the client a follow-up query.
- `addEmployee` has a selection set (`{ employeeId firstName ... }`) because it
  returns an object type. You still choose which fields come back.

---

## Step 4.2 — Break it: forget to commit

This one catches everybody, and it fails *silently*.

**Type** — comment out the commit:

```python
        # connection.commit()
```

**Run** — restart, then add another employee via the mutation. It appears to
succeed — you get an `employeeId` back and no error at all.

Now query for it:

```graphql
query { employees { employeeId firstName } }
```

**It isn't there.**

**What just happened**

`sqlite3` opens a transaction implicitly for `INSERT`/`UPDATE`/`DELETE`.
Closing the connection without `commit()` **rolls the transaction back**. Your
INSERT was discarded, and nothing warned you — the mutation still returned a
plausible id, because `lastrowid` was set before the rollback.

**Restore the `connection.commit()` line** and re-run. Every mutation that
changes data needs it.

Reset your data before continuing:

```bash
uv run python tutorial/create_database.py
```

---

## Step 4.3 — `updateEmployee` → `UPDATE`

**Type** — add inside `Mutation`:

```python
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
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        sql = """
            UPDATE Employee_Base_0
            SET first_name = ?, last_name = ?, age = ?, gender = ?,
                position = ?, salary = ?, city = ?
            WHERE employee_id = ?
        """
        print(f"\n  RESOLVER  update_employee({employee_id})")
        print(f"  SQL       UPDATE Employee_Base_0 ... WHERE employee_id = ?")

        cursor.execute(
            sql,
            (first_name, last_name, age, gender, position, salary, city, employee_id),
        )
        connection.commit()

        rows_changed = cursor.rowcount
        print(f"  ROWS      {rows_changed} changed")
        connection.close()

        if rows_changed == 0:
            return None

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
```

**Run** — restart. In GraphiQL:

```graphql
mutation {
  updateEmployee(
    employeeId: 3
    firstName: "Robert"
    lastName: "Brown"
    age: 30
    gender: "Male"
    position: "Senior Analyst"
    salary: 80000.00
    city: "Boston"
  ) {
    employeeId
    firstName
    position
    salary
  }
}
```

**What just happened**

Every field is required — this is a **full-record update**. Partial updates
("change only the salary") need extra machinery: optional arguments, a
dynamically built `SET` clause, or a separate input type. Deliberately out of
scope; get the basic shape first.

`cursor.rowcount` tells you how many rows the `UPDATE` actually touched. Try
`employeeId: 999`:

```json
{ "data": { "updateEmployee": null } }
```

Terminal A shows `ROWS 0 changed`. Same pattern as `employee(id: 999)` — a
`null`, not an error.

---

## Step 4.4 — `deleteEmployee` → `DELETE`

**Type** — add inside `Mutation`:

```python
    @strawberry.mutation
    def delete_employee(self, employee_id: int) -> bool:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        sql = "DELETE FROM Employee_Base_0 WHERE employee_id = ?"
        print(f"\n  RESOLVER  delete_employee({employee_id})")
        print(f"  SQL       {sql}   params=({employee_id},)")

        cursor.execute(sql, (employee_id,))
        connection.commit()

        rows_deleted = cursor.rowcount
        print(f"  ROWS      {rows_deleted} deleted")
        connection.close()

        return rows_deleted > 0
```

**Run** — restart. In GraphiQL:

```graphql
mutation {
  deleteEmployee(employeeId: 10)
}
```

```json
{ "data": { "deleteEmployee": true } }
```

Run it a second time → `false`. Nothing was there to delete.

**What just happened**

This mutation returns `Boolean!`, a **scalar**, not an object type. So it has
**no selection set** — no braces after it. That is not a special rule for
mutations; it follows from the type. Prove it:

```graphql
mutation { deleteEmployee(employeeId: 999) { ok } }
```

```text
Field 'deleteEmployee' must not have a selection since type 'Boolean!' has no subfields.
```

**Phase 4 done.** You now have the complete mapping:

| GraphQL operation | Your resolver | SQL |
|---|---|---|
| `employees` | `employees()` | `SELECT` |
| `employee(id)` | `employee(id)` | `SELECT ... WHERE` |
| `addEmployee(...)` | `add_employee()` | `INSERT` |
| `updateEmployee(...)` | `update_employee()` | `UPDATE` |
| `deleteEmployee(...)` | `delete_employee()` | `DELETE` |

Reset your data: `uv run python tutorial/create_database.py`

---

# Phase 5 — curl: GraphQL Is Just HTTP

**~25 minutes.** GraphiQL is convenient, and convenience hides mechanism. Time
to send the raw HTTP yourself.

## Step 5.1 — Give the server a real endpoint

Your server currently answers on `/`. Real GraphQL servers expose one named
endpoint, `/graphql`.

**Type** — add to the imports:

```python
from starlette.applications import Starlette
from starlette.routing import Route
```

**Type** — replace `app = GraphQL(schema)` with:

```python
graphql_app = GraphQL(schema)

app = Starlette(
    routes=[Route("/graphql", graphql_app, methods=["GET", "POST"])],
)
```

**Run** — restart. GraphiQL now lives at <http://localhost:8009/graphql>, and
`http://localhost:8009/` returns "Not Found".

> **Why `Route` and not `Mount`?** `Mount("/graphql", ...)` would answer
> `/graphql/` and issue a 307 redirect for `/graphql`. Every curl command below
> would need `-L`. `Route` matches the exact path — which is what you want for
> an API endpoint.

---

## Step 5.2 — Query with curl

**Run** — in **Terminal B**:

```bash
curl -X POST http://localhost:8009/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query { employees { employeeId firstName lastName city } }"}'
```

Watch Terminal A: your resolver runs and prints its SQL, exactly as it did for
the browser.

**What just happened**

A GraphQL request is nothing exotic:

- `POST` to one URL
- `Content-Type: application/json`
- a JSON body with a `"query"` string (and optionally `"variables"`)

The GraphQL document is *data inside the body*. The HTTP layer knows nothing
about employees.

---

## Step 5.3 — The three mutations

**INSERT:**

```bash
curl -X POST http://localhost:8009/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { addEmployee(firstName: \"Alice\", lastName: \"Cooper\", age: 34, gender: \"Female\", position: \"Engineer\", salary: 102000.00, city: \"Houston\") { employeeId firstName } }"}'
```

**UPDATE:**

```bash
curl -X POST http://localhost:8009/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { updateEmployee(employeeId: 3, firstName: \"Robert\", lastName: \"Brown\", age: 30, gender: \"Male\", position: \"Senior Analyst\", salary: 80000.00, city: \"Boston\") { employeeId position salary } }"}'
```

**DELETE:**

```bash
curl -X POST http://localhost:8009/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { deleteEmployee(employeeId: 11) }"}'
```

**Variables** travel in their own JSON key:

```bash
curl -X POST http://localhost:8009/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query GetEmployee($id: Int!) { employee(id: $id) { employeeId firstName position } }","variables":{"id":5}}'
```

## Step 5.4 — The realisation

Look back at those four commands. **Compare what changed:**

| | REST would use | GraphQL uses |
|---|---|---|
| Read all | `GET /employees` | `POST /graphql` |
| Read one | `GET /employees/5` | `POST /graphql` |
| Create | `POST /employees` | `POST /graphql` |
| Update | `PUT /employees/3` | `POST /graphql` |
| Delete | `DELETE /employees/10` | `POST /graphql` |

**One URL. One HTTP method. Every time.** The URL and verb carry no meaning —
the GraphQL document in the body decides everything. That is the shift: the
API's semantics moved out of HTTP and into the schema.

**Optional** — see the headers:

```bash
curl -i -X POST http://localhost:8009/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ employees { employeeId } }"}'
```

Note `HTTP/1.1 200 OK` even for a *failed* GraphQL query. Try it with a bad
field name — still `200`, with an `errors` array in the body. GraphQL reports
its own errors in the payload, not in the HTTP status.

---

# Phase 6 — Apollo Client in the Browser

**~40 minutes.** Same server, same operations, driven from JavaScript.

## Step 6.1 — A page that runs one query

**Type** — `tutorial/index.html`:

```html
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>My GraphQL Client</title></head>
<body>
  <h1>Employees</h1>
  <button id="load">Load employees</button>
  <pre id="out"></pre>

<script type="module">
import {
  ApolloClient, InMemoryCache, HttpLink, gql
} from "https://cdn.jsdelivr.net/npm/@apollo/client@3.13.8/+esm";

const client = new ApolloClient({
  link: new HttpLink({ uri: "http://localhost:8009/graphql" }),
  cache: new InMemoryCache(),
  defaultOptions: { query: { fetchPolicy: "no-cache" } },
});

const LIST_EMPLOYEES = gql`
  query ListEmployees {
    employees {
      employeeId
      firstName
      lastName
      position
      city
    }
  }
`;

document.getElementById("load").onclick = async () => {
  const result = await client.query({ query: LIST_EMPLOYEES });
  document.getElementById("out").textContent =
    JSON.stringify(result.data, null, 2);
};
</script>
</body>
</html>
```

**Run** — open it directly from disk:

```bash
open tutorial/index.html
```

Click **Load employees**.

## Step 6.2 — Break it: the CORS wall

**It fails.** Nothing appears. Open the browser devtools **Console** (⌥⌘I on
macOS) and you will see something like:

```text
Access to fetch at 'http://localhost:8009/graphql' from origin 'null'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header
is present on the requested resource.
```

Now check **Terminal A**. Depending on the browser you may see no resolver
output at all — the request was blocked before it ever mattered.

**What just happened**

Your page was loaded from `file://`, so its origin is `null`. Your server is
`http://localhost:8009`. Different origins. The **browser** refuses to hand the
response to JavaScript unless the server explicitly opts in.

This is a browser rule, not a GraphQL rule — which is why `curl` never hit it.
`curl` has no origin and enforces no same-origin policy.

**Fix it.** In `tutorial/server.py`, add to the imports:

```python
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
```

and extend the `Starlette(...)` call:

```python
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
```

**Run** — restart Terminal A, reload the page, click again. Ten employees.

> `allow_origins=["*"]` means *any* website may call this server. Fine for a
> local tutorial; for anything real you list the origins you actually trust.

---

## Step 6.3 — Watch the network

Open devtools → **Network** tab → click **Load employees**.

Click the `graphql` request and inspect:

- **Headers** — `POST`, URL `http://localhost:8009/graphql`
- **Payload** — `{"operationName":"ListEmployees","variables":{},"query":"query ListEmployees {\n  employees {\n ..."}`
- **Response** — the JSON your resolver produced

**What just happened**

The `gql` tagged template in your JavaScript became *exactly* the kind of HTTP
request you sent by hand with `curl` in Phase 5. Apollo is a convenience layer
over the same POST. Nothing magic is happening — and now you have seen it.

You may also spot an `OPTIONS` request just before the `POST`. That is the CORS
**preflight**: the browser asking permission before sending the real request.
Your `CORSMiddleware` answers it.

---

## Step 6.4 — A mutation with variables

**Type** — add before the closing `</script>`:

```javascript
const ADD_EMPLOYEE = gql`
  mutation AddEmployee(
    $firstName: String!
    $lastName: String!
    $age: Int!
    $gender: String!
    $position: String!
    $salary: Float!
    $city: String!
  ) {
    addEmployee(
      firstName: $firstName
      lastName: $lastName
      age: $age
      gender: $gender
      position: $position
      salary: $salary
      city: $city
    ) {
      employeeId
      firstName
      lastName
    }
  }
`;

document.getElementById("add").onclick = async () => {
  const result = await client.mutate({
    mutation: ADD_EMPLOYEE,
    variables: {
      firstName: document.getElementById("f-first").value,
      lastName:  document.getElementById("f-last").value,
      age:       Number(document.getElementById("f-age").value),
      gender:    "Female",
      position:  "Engineer",
      salary:    102000.0,
      city:      "Houston",
    },
  });
  document.getElementById("out").textContent =
    JSON.stringify(result.data, null, 2);
};
```

**Type** — add the form, just above the `<pre id="out">`:

```html
  <h2>Add an employee</h2>
  <input id="f-first" placeholder="firstName" value="Alice">
  <input id="f-last"  placeholder="lastName"  value="Cooper">
  <input id="f-age"   placeholder="age"       value="34" type="number">
  <button id="add">Add</button>
```

**Run** — reload the page (no server restart needed; you only changed HTML).
Click **Add**, then **Load employees**.

**What just happened**

- `client.query()` for reads, `client.mutate()` for writes.
- Variables are passed as a plain JS object — no string building, so no
  escaping bugs and no injection risk in the query itself.
- Look at the Network payload again: `"variables":{"firstName":"Alice",...}`
  is a separate JSON key from `"query"`. Exactly like your curl command in
  Step 5.3.

**Note `fetchPolicy: "no-cache"`.** Apollo caches aggressively by default.
Without that setting, clicking **Load employees** after an insert can return
the *old* list from cache. Caching is a genuine Apollo strength, but it hides
the request/response cycle you are here to learn. Remove it later, once the
basics are automatic.

---

## Step 6.5 — Finish it yourself

You now have every pattern you need. Add, on your own:

1. **Get one employee** — a number input + `employee(id: $id)` query.
   *Hint:* handle the `null` case when the id doesn't exist.
2. **Update** — a form with all eight fields + `updateEmployee`.
3. **Delete** — a number input + `deleteEmployee`.
   *Hint:* the mutation returns a Boolean, so no selection set.

Stuck? The reference implementation is [frontend/index.html](frontend/index.html).

---

# Phase 7 — Review

**~10 minutes.** Close the files and answer these from memory. If one is
shaky, go back to the phase in brackets.

1. What is a GraphQL **schema**, and where did yours come from? *[2.1]*
2. Why did asking for fewer fields not change the SQL? *[3.1]*
3. What happens when you query a field that doesn't exist — and does your
   database ever hear about it? *[3.2]*
4. What does `employee(id: 999)` return, and why isn't that an error? *[3.3]*
5. What is the difference between an **argument** and a **variable**? *[3.4]*
6. Why must `?` placeholders be used instead of string concatenation? *[3.3]*
7. Why does `addEmployee` return an Employee, but `deleteEmployee` return a
   Boolean — and why does only one of them take a selection set? *[4.1, 4.4]*
8. What happens if you forget `connection.commit()`? *[4.2]*
9. What is the HTTP method and URL for a GraphQL delete? *[5.4]*
10. Why did `curl` work but the browser page get blocked? *[6.2]*

### Trace it end to end

Say this out loud, from memory, then check it against Terminal A by running the
query one more time:

```text
GraphQL          employee(id: 5)
                        |
Resolver         Query.employee(5)
                        |
SQL              SELECT * FROM Employee_Base_0 WHERE employee_id = ?
                        |
SQLite row       (5, 'David', 'Miller', 46, 'Male', 'Architect', 145000.0, 'Denver')
                        |
Employee object  Employee(employee_id=5, first_name='David', ...)
                        |
JSON response    {"data": {"employee": {"firstName": "David", ...}}}
```

### The mental model

```text
Apollo Client / curl / GraphQL IDE
              |
              |  GraphQL document (in an HTTP POST body)
              v
         GraphQL Schema          <- validates before anything runs
              |
              v
           Resolver              <- your plain Python function
              |
              |  parameterized SQL
              v
            SQLite
```

```text
SQL SELECT  ≈  GraphQL Query
SQL INSERT  ≈  GraphQL Mutation
SQL UPDATE  ≈  GraphQL Mutation
SQL DELETE  ≈  GraphQL Mutation
```

The **schema** is the API you present to clients. The **resolver** is the bridge
between that schema and your data. Everything else in GraphQL is an elaboration
of those two ideas.

---

## Compare your work

Your `tutorial/server.py` should now be functionally identical to
[graphql_server.py](graphql_server.py) — minus the `print()` calls, and with
one refactor worth studying: the reference version pulls the eight-line
row-to-`Employee` conversion into a single `row_to_employee(row)` helper,
because you wrote it five times. Read it and see whether you agree with the
trade-off.

## Where to go next

You deliberately skipped a lot. In rough order of usefulness:

- **Partial updates** — optional arguments, or a dedicated input type
- **Input types** — `addEmployee(input: EmployeeInput!)` instead of 7 arguments
- **Connection handling** — one connection per request rather than per resolver
- **The N+1 problem and DataLoader** — the first thing that bites on nested types
- **Pagination, filtering, sorting** — arguments on `employees`
- **Apollo caching** — remove `no-cache` and learn normalization
- **Errors** — when to return `null` vs. raise a real GraphQL error

Every one of those makes sense only once the path you just built —
**document → schema → resolver → SQL** — is second nature.
