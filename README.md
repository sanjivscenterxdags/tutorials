# GraphQL Absolute Basics — a 3-hour tutorial

A deliberately tiny GraphQL application: **Strawberry GraphQL resolvers talking
straight to SQLite**, exercised three ways — the browser GraphQL IDE, `curl`,
and a minimal Apollo Client page.

There is no ORM, no REST layer, and no service/repository classes, so you can
follow one GraphQL operation all the way down to its SQL statement:

```text
Browser GraphQL IDE / curl / Apollo Client
              |
              |  GraphQL query or mutation  (HTTP POST)
              v
        /graphql endpoint
              |
              v
     Strawberry GraphQL server
              |
              v
      Resolver function (plain Python)
              |
              |  parameterized SQL
              v
        SQLite  (employees.db / Employee_Base_0)
              |
              v
        GraphQL JSON response
```

**Two ways to use this repo:**

- **Learn by typing it yourself** → [TUTORIAL.md](TUTORIAL.md). Builds everything
  from scratch in a `tutorial/` directory, with deliberate break-it-and-see
  detours. ~3 hours. This is the one to do.
- **Run the finished code** → keep reading below.

See [SPEC.md](SPEC.md) for the full specification.

---

## Files

| File | What it is |
|---|---|
| [TUTORIAL.md](TUTORIAL.md) | **Start here to learn.** A type-it-yourself walkthrough that builds all of this from an empty directory |
| [create_database.py](create_database.py) | Creates `employees.db`, the `Employee_Base_0` table, and ten sample rows |
| [graphql_server.py](graphql_server.py) | The whole GraphQL server: type, schema, five resolvers, `/graphql` endpoint |
| [requirements.txt](requirements.txt) | The two dependencies |
| [frontend/index.html](frontend/index.html) | Minimal Apollo Client page — no npm, no build step |
| [SPEC.md](SPEC.md) | The specification this project implements |

---

## The mapping the tutorial is about

| GraphQL operation | Resolver | SQL |
|---|---|---|
| `employees` | `get_employees()` | `SELECT` |
| `employee(id)` | `get_employee()` | `SELECT ... WHERE` |
| `addEmployee(...)` | `add_employee()` | `INSERT` |
| `updateEmployee(...)` | `update_employee()` | `UPDATE` |
| `deleteEmployee(...)` | `delete_employee()` | `DELETE` |

SQLite uses `snake_case`; GraphQL uses `camelCase`. Strawberry converts:

```text
employee_id  ->  employeeId
first_name   ->  firstName
last_name    ->  lastName
```

---

## 1. Create the Python environment

This project uses [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

Or with plain `venv` + `pip`:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
```

## 2. Install dependencies

Already done by `uv sync`. With pip:

```bash
pip install -r requirements.txt
```

## 3. Create the database

```bash
uv run python create_database.py     # or: python create_database.py
```

This drops and recreates `Employee_Base_0`, inserts ten employees, and prints
them back so you can see the data. It is safe to re-run at any time — that is
your reset button.

## 4. Start the GraphQL server

```bash
uv run python graphql_server.py      # or: python graphql_server.py
```

```text
GraphQL IDE:  http://localhost:8008/graphql
Endpoint:     POST http://localhost:8008/graphql
```

Leave this running in its own terminal.

> **Port 8008, not 8000.** Port 8000 is a very common default and was already
> taken on the development machine (by Docker), which produces confusing
> responses from the wrong server. To change it, edit the `PORT` constant at the
> top of [graphql_server.py](graphql_server.py) — and remember to update the URL
> in [frontend/index.html](frontend/index.html) to match.

## 5. Open the GraphQL browser IDE

Visit <http://localhost:8008/graphql> in a browser. GraphiQL loads at the same
URL that serves the API. Use the **Docs** panel on the right to browse the
schema Strawberry generated.

---

## 6. The GraphQL examples

Run each of these in the IDE and read **both** the request and the JSON
response.

### 6.1 Query all employees

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

Now delete `position` and `city` from the query and run it again. The resolver
did not change — it still runs `SELECT *` — but the JSON response shrank. That
is **GraphQL field selection**: the client decides what comes back.

### 6.2 Query one employee

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

Try `id: 999`. You get `"employee": null` — not an error.

### 6.3 Add an employee

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

You never sent an `employeeId` — SQLite generated it with `AUTOINCREMENT`, and
the mutation returns the row it just created.

### 6.4 Update an employee

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
    lastName
    position
    salary
  }
}
```

Every field is required — this is a full-record update. Partial updates are a
more advanced topic and are deliberately left out.

### 6.5 Delete an employee

```graphql
mutation {
  deleteEmployee(employeeId: 11)
}
```

```json
{ "data": { "deleteEmployee": true } }
```

The return type is `Boolean!`, not an object, so there is no selection set.
Run it a second time and you get `false` — nothing was deleted.

### 6.6 Using GraphQL variables

Everything above used literal values written inside the operation. Real clients
usually send **variables** instead. Put this in the IDE's query pane:

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

and this in the **Variables** pane at the bottom:

```json
{ "id": 5 }
```

Same result, but now the query text is fixed and only the data changes. This is
how [frontend/index.html](frontend/index.html) calls every operation.

---

## 7. The curl examples

Every command below is a `POST` to the **same URL**. Only the GraphQL document
inside the JSON body changes — that is the whole point.

### 7.1 SELECT / Query

```bash
curl -X POST http://localhost:8008/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query { employees { employeeId firstName lastName position salary city } }"}'
```

### 7.2 INSERT / Mutation

```bash
curl -X POST http://localhost:8008/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { addEmployee(firstName: \"Alice\", lastName: \"Cooper\", age: 34, gender: \"Female\", position: \"Engineer\", salary: 102000.00, city: \"Houston\") { employeeId firstName lastName position } }"}'
```

### 7.3 UPDATE / Mutation

```bash
curl -X POST http://localhost:8008/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { updateEmployee(employeeId: 3, firstName: \"Robert\", lastName: \"Brown\", age: 30, gender: \"Male\", position: \"Senior Analyst\", salary: 80000.00, city: \"Boston\") { employeeId firstName position salary } }"}'
```

### 7.4 DELETE / Mutation

```bash
curl -X POST http://localhost:8008/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { deleteEmployee(employeeId: 11) }"}'
```

### 7.5 Query with variables

Variables travel in their own JSON key, next to `query`:

```bash
curl -X POST http://localhost:8008/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query GetEmployee($id: Int!) { employee(id: $id) { employeeId firstName lastName position } }","variables":{"id":5}}'
```

Notice what is **not** happening here: there is no `/employees/5`, no `GET`,
no `PUT`, no `DELETE` verb. There is one URL and one HTTP method, and the
GraphQL document decides the operation.

---

## 8. The Apollo Client frontend

With the server still running, open the page:

```bash
open frontend/index.html          # macOS
# xdg-open frontend/index.html    # Linux
# start frontend\index.html       # Windows
```

Opening the file directly from disk works because the server enables CORS.
If you prefer to serve it over HTTP, use a second terminal:

```bash
python3 -m http.server 5500 --directory frontend
# then visit http://localhost:5500
```

The page has five sections — list, get one, add, update, delete — and each one
**prints the exact `gql` document it is about to send** in a grey box above the
button. Apollo is never allowed to hide the GraphQL from you.

Open your browser devtools **Network** tab and click through the buttons. Every
single request is `POST /graphql`; only the request body differs. That is the
same lesson as the curl section, seen from JavaScript:

```text
JavaScript / Apollo Client
          |
          |  gql` query {...} `
          v
   GraphQL HTTP request
          |
          v
        Server
          |
          v
        SQLite
          |
          v
    JSON response
          |
          v
    Apollo Client
          |
          v
        HTML
```

---

## 9. Tracing one operation end to end

This is the exercise worth doing at least once by hand:

```text
GraphQL:

    employee(id: 5)

            ↓

Resolver:   graphql_server.py -> Query.employee

    get_employee(5)

            ↓

SQL:

    SELECT * FROM Employee_Base_0 WHERE employee_id = 5

            ↓

SQLite row:

    (5, 'David', 'Miller', 46, 'Male', 'Architect', 145000.0, 'Denver')

            ↓

Employee GraphQL object:   row_to_employee(row)

            ↓

JSON response:

    { "data": { "employee": { "firstName": "David", ... } } }
```

Open [graphql_server.py](graphql_server.py) and read `Query.employee`. Every
step above is a numbered line in that one function.

---

## 10. A note on parameterized SQL

Every resolver passes client input to SQLite as a **parameter**, never by
building a SQL string:

```python
# correct
cursor.execute(
    "SELECT * FROM Employee_Base_0 WHERE employee_id = ?",
    (employee_id,),
)

# never do this
cursor.execute(
    "SELECT * FROM Employee_Base_0 WHERE employee_id = " + employee_id
)
```

The `?` placeholder keeps data and code separate, which is what prevents SQL
injection. That is as far as this tutorial goes on security — but it is a habit
worth forming from the first line of SQL you write.

---

## 11. Suggested three-hour sequence

| Phase | Time | What you do |
|---|---:|---|
| 1 — Database | 15 min | Run `create_database.py`, read the ten rows |
| 2 — Schema | 20 min | Read `graphql_server.py` §1: the `Employee` type, Query, Mutation, fields, arguments |
| 3 — Query resolvers | 30 min | `employees`, `employee(id)` in the IDE (§6.1–6.2) |
| 4 — Mutation resolvers | 40 min | `addEmployee`, `updateEmployee`, `deleteEmployee` in the IDE (§6.3–6.5) |
| 5 — curl | 25 min | All four curl commands (§7); notice every one is `POST /graphql` |
| 6 — Apollo Client | 40 min | Open the frontend (§8), watch the Network tab, find each `gql` statement |
| 7 — Review | 10 min | Explain: schema, type, query, mutation, resolver, argument, variable, endpoint, JSON response, Apollo Client |

---

## 12. What you should be able to say at the end

```text
Apollo Client / curl / GraphQL IDE
              |
              |  GraphQL
              v
         GraphQL Schema
              |
              v
           Resolver
              |
              |  SQL
              v
            SQLite
```

```text
SQL SELECT  ≈  GraphQL Query
SQL INSERT  ≈  GraphQL Mutation
SQL UPDATE  ≈  GraphQL Mutation
SQL DELETE  ≈  GraphQL Mutation
```

The GraphQL server is the **semantic API** presented to the client. The
resolver is the **implementation bridge** between that schema and SQLite.

---

## Troubleshooting

**`employees.db not found`** — run `python create_database.py` first.

**The server answers, but with strange errors you did not write** — something
else is listening on that port. Check with `lsof -nP -iTCP:8008 -sTCP:LISTEN`
and change the `PORT` constant in `graphql_server.py` if needed.

**The frontend shows a network/CORS error** — the server is not running, or it
is on a different port than the `GRAPHQL_ENDPOINT` constant in
`frontend/index.html`.

**You want a clean slate** — re-run `python create_database.py`.
