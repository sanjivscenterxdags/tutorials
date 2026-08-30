# SPEC.md — GraphQL Absolute-Basics Tutorial

Distilled, buildable specification derived from
[docs/graphql_absolute_basics_architecture_requirements.md](docs/graphql_absolute_basics_architecture_requirements.md).

---

## 1. Overview & Learning Goal

Build a deliberately small GraphQL learning application, completable and
understandable in ~3 hours. The learner must be able to trace one GraphQL
operation end-to-end without crossing abstraction layers:

```text
Browser GraphQL IDE / curl / Apollo Client
              |
              | GraphQL query or mutation (HTTP POST)
              v
        /graphql endpoint
              |
              v
     Strawberry GraphQL server
              |
              v
      Resolver function (plain Python)
              |
              | parameterized SQL
              v
        SQLite  (employees.db / Employee_Base_0)
              |
              v
      Resolver result -> Employee object
              |
              v
        GraphQL JSON response
```

**Key architectural principle:** GraphQL resolvers talk *directly* to SQLite.
There is no intermediate REST API layer, no ORM, no service/repository classes.

**Guiding philosophy:**

```text
clarity > abstraction
visibility > framework magic
small code > production architecture
direct SQL > ORM
one endpoint > multiple API layers
learning GraphQL > building infrastructure
```

---

## 2. Scope

### In scope

- One GraphQL endpoint: `POST /graphql` (plus its browser IDE at the same path)
- GraphQL schema: one object type (`Employee`), two queries, three mutations
- Resolvers as plain Python functions with visible, parameterized SQL
- SQLite database with one table and ten seed rows
- Browser GraphQL IDE exercises (GraphiQL, served by Strawberry)
- Working `curl` examples for all CRUD categories
- One GraphQL-variables example (after literal-value examples)
- Minimal single-file Apollo Client frontend (CDN scripts, no build step)
- Minimal error handling (null / false / default GraphQL errors)

### Explicitly excluded (do not implement)

REST APIs, FastAPI CRUD endpoints, authentication, authorization, JWT, OAuth,
RBAC, any ORM (SQLAlchemy, Django ORM, Prisma, Peewee), PostgreSQL, MySQL,
Redis, Kafka, Docker, Kubernetes, GraphQL subscriptions, WebSockets,
federation, DataLoader, batching, advanced caching, pagination, sorting,
complex filtering, interfaces, unions, fragments-as-a-topic, microservices,
gateway architecture, production deployment, enterprise logging, extensive
automated tests, CI/CD, repository/service/DAO classes, dependency injection,
custom error frameworks.

---

## 3. Technology Stack

| Layer | Choice | Notes |
|---|---|---|
| Language | Python 3.12+ | matches existing `pyproject.toml` |
| Database | SQLite via built-in `sqlite3` | **no ORM** — SQL stays visible in resolvers |
| GraphQL server | `strawberry-graphql[asgi]` | schema, resolvers, GraphiQL IDE; the `[asgi]` extra supplies Starlette (routing + CORS) |
| ASGI runner | `uvicorn` | serves the ASGI app on `http://localhost:8008` |
| Frontend | Single `frontend/index.html` | Apollo Client as an ES module from a CDN; vanilla JS, no React, no npm, no bundler |

**Port:** `8008`. All examples use `http://localhost:8008/graphql`.

> Changed from the originally specified 8000 during implementation: port 8000
> was already bound on the development machine (a Docker container on the IPv6
> wildcard), so `localhost:8000` silently reached the wrong server. The port is
> a single `PORT` constant at the top of `graphql_server.py`.

**Routing:** the endpoint must be an exact-match route, not a Starlette `Mount`.
A `Mount("/graphql", ...)` issues a 307 redirect from `/graphql` to `/graphql/`,
which breaks the plain `POST /graphql` that the curl exercises depend on. Use
`Route("/graphql", graphql_app, methods=["GET", "POST"])`.

**CORS:** the server must allow cross-origin requests so the Apollo Client
page (opened from `file://` or a separate static port) can call `/graphql`.
Use the minimal CORS support available in the chosen ASGI setup — nothing more.

**Dependency files (project adaptation):** the requirements doc asks for
`requirements.txt`; this project is `uv`-managed. Provide **both**:

- `pyproject.toml` dependencies (primary, via `uv add "strawberry-graphql[asgi]" uvicorn`)
- `requirements.txt` containing only `strawberry-graphql[asgi]` and `uvicorn`
  (tutorial fidelity for non-uv readers)

---

## 4. Data Model

### Database

- File: `employees.db` (project root)
- Table: `Employee_Base_0`

### DDL

```sql
CREATE TABLE Employee_Base_0 (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name  TEXT    NOT NULL,
    last_name   TEXT    NOT NULL,
    age         INTEGER NOT NULL,
    gender      TEXT    NOT NULL,
    position    TEXT    NOT NULL,
    salary      REAL    NOT NULL,
    city        TEXT    NOT NULL
);
```

### Seed data (exactly 10 rows)

| employee_id | first_name | last_name | age | gender | position | salary | city |
|---:|---|---|---:|---|---|---:|---|
| 1 | John | Smith | 38 | Male | Engineer | 95000.00 | Dallas |
| 2 | Mary | Jones | 42 | Female | Manager | 125000.00 | Chicago |
| 3 | Robert | Brown | 29 | Male | Analyst | 72000.00 | Boston |
| 4 | Linda | Wilson | 35 | Female | Developer | 98000.00 | Austin |
| 5 | David | Miller | 46 | Male | Architect | 145000.00 | Denver |
| 6 | Susan | Davis | 31 | Female | Consultant | 88000.00 | Atlanta |
| 7 | James | Anderson | 40 | Male | Project Manager | 118000.00 | Seattle |
| 8 | Karen | Thomas | 27 | Female | Engineer | 84000.00 | Phoenix |
| 9 | Michael | Jackson | 51 | Male | Director | 165000.00 | New York |
| 10 | Patricia | Martin | 37 | Female | Product Manager | 110000.00 | Miami |

### Initialization behavior

`create_database.py` must be **repeatable**: it drops/recreates the table
(acceptable per the requirements for an introductory tutorial), inserts the
ten rows, and prints a verification `SELECT` so the learner sees the data.

### Column ↔ field mapping (must be made visible in code/README)

```text
SQLite column      GraphQL field
employee_id   ->   employeeId
first_name    ->   firstName
last_name     ->   lastName
age           ->   age
gender        ->   gender
position      ->   position
salary        ->   salary
city          ->   city
```

---

## 5. GraphQL API Contract

The logical schema (Strawberry syntax may differ; the interface must stay
equivalent):

```graphql
type Employee {
  employeeId: Int!
  firstName: String!
  lastName: String!
  age: Int!
  gender: String!
  position: String!
  salary: Float!
  city: String!
}

type Query {
  employees: [Employee!]!
  employee(id: Int!): Employee
}

type Mutation {
  addEmployee(
    firstName: String!
    lastName: String!
    age: Int!
    gender: String!
    position: String!
    salary: Float!
    city: String!
  ): Employee!

  updateEmployee(
    employeeId: Int!
    firstName: String!
    lastName: String!
    age: Int!
    gender: String!
    position: String!
    salary: Float!
    city: String!
  ): Employee

  deleteEmployee(employeeId: Int!): Boolean!
}
```

### Semantics

| Operation | Behavior |
|---|---|
| `employees` | Return all rows. Client field selection must work (demonstrated in exercises). |
| `employee(id)` | Return the matching employee, or `null` if not found. |
| `addEmployee(...)` | Insert row; `employee_id` generated by SQLite; return the newly created employee (re-read by `lastrowid`). |
| `updateEmployee(...)` | Full-record update (all fields required — no partial-update semantics). Return the updated employee, or `null` if the id does not exist. |
| `deleteEmployee(employeeId)` | Return `true` if a row was deleted, `false` if the id does not exist. |

### Error handling (keep minimal)

- Nonexistent employee on query/update → `null`
- Nonexistent employee on delete → `false`
- Invalid GraphQL syntax → default GraphQL error structure (do nothing custom)

---

## 6. Resolver Design Rules

Resolvers are **plain Python functions** in `graphql_server.py`. Each resolver
visibly performs, in order:

```text
1. open sqlite3 connection to employees.db
2. execute parameterized SQL
3. fetch row(s)
4. convert row(s) to Employee object(s)
5. commit (mutations) and close connection
6. return result
```

### GraphQL → resolver → SQL mapping (a primary instructional objective)

| GraphQL Operation | Resolver | SQL |
|---|---|---|
| `employees` | `get_employees()` | `SELECT * FROM Employee_Base_0;` |
| `employee(id)` | `get_employee(id)` | `SELECT * FROM Employee_Base_0 WHERE employee_id = ?;` |
| `addEmployee(...)` | `add_employee(...)` | `INSERT INTO Employee_Base_0 (first_name, last_name, age, gender, position, salary, city) VALUES (?, ?, ?, ?, ?, ?, ?);` |
| `updateEmployee(...)` | `update_employee(...)` | `UPDATE Employee_Base_0 SET first_name=?, last_name=?, age=?, gender=?, position=?, salary=?, city=? WHERE employee_id = ?;` |
| `deleteEmployee(id)` | `delete_employee(id)` | `DELETE FROM Employee_Base_0 WHERE employee_id = ?;` |

### Hard rules

- **All SQL taking client input uses `?` parameter substitution.** Never build
  SQL with string concatenation or f-strings (basic SQL-injection awareness).
- No repository classes, service classes, DAO layers, dependency injection,
  or generic database abstractions.
- Comments in resolvers connect GraphQL operation → SQL statement explicitly.

---

## 7. Deliverables & File Layout

```text
gqL/                          (this repo)
├── SPEC.md                   (this file)
├── employees.db              generated by create_database.py (not committed)
├── create_database.py        Deliverable 1
├── graphql_server.py         Deliverable 2
├── requirements.txt          Deliverable 3
├── README.md                 Deliverable 5 (replaces stub)
├── pyproject.toml            existing; gains strawberry-graphql + uvicorn
├── docs/
│   └── graphql_absolute_basics_architecture_requirements.md
└── frontend/
    └── index.html            Deliverable 4
```

| # | File | Responsibilities |
|---|---|---|
| 1 | `create_database.py` | Create `employees.db`, create `Employee_Base_0`, insert the 10 seed rows, print verification output. Repeatable (drop & recreate). |
| 2 | `graphql_server.py` | Define `Employee` type, `Query`, `Mutation`, the five resolvers with inline SQL; expose `/graphql` with GraphiQL; runnable via `uvicorn`. |
| 3 | `requirements.txt` | Only `strawberry-graphql[asgi]` and `uvicorn`. |
| 4 | `frontend/index.html` | Single-file Apollo Client app (CDN). Sections for: list employees, get one by id, add (form), update (form), delete (by id). The `gql` query/mutation text must be visible in the page source — Apollo must not hide the GraphQL from the learner. No styling beyond bare-minimum layout. |
| 5 | `README.md` | Exact commands for: env creation, dependency install (uv and pip/requirements.txt paths), database creation, server start, opening GraphiQL, every GraphQL example, every curl example, opening the frontend. Repeats the conceptual flow diagrams (GraphQL → resolver → SQL → JSON). |

Additional files only when necessary for clarity; no framework-generated
directory trees.

---

## 8. Exercises the Artifacts Must Support

### 8.1 Browser GraphQL IDE (GraphiQL at /graphql)

Five operations, inspecting both the GraphQL request and the JSON response:

1. Query all employees (with field selection — request fewer fields than exist)
2. Query one employee by id
3. Add one employee
4. Update one employee
5. Delete one employee

### 8.2 curl (all against `http://localhost:8008/graphql`)

Working commands provided in README for:

1. Query (`employees`)
2. INSERT mutation (`addEmployee`)
3. UPDATE mutation (`updateEmployee`)
4. DELETE mutation (`deleteEmployee`)

The learner must be able to see the GraphQL request body in each command, and
observe that every operation is `POST /graphql` — the GraphQL document, not
the URL/verb, determines the operation.

### 8.3 GraphQL variables (one example, after literals)

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

with variables `{ "id": 5 }`. No input-object patterns beyond this.

### 8.4 Apollo Client frontend

- List employees (show at least employeeId, firstName, lastName, position, city)
- Retrieve one by entered id
- Insert via minimal form (all seven writable fields)
- Update via minimal form (id + all seven fields)
- Delete by entered id
- The learner can identify the exact `gql` statement behind each request

---

## 9. Acceptance Criteria (Definition of Done)

- [ ] `create_database.py` runs repeatedly without error; `employees.db`
      contains exactly the 10 seed rows after each run
- [ ] `uvicorn`-served app exposes `/graphql` with a working GraphiQL IDE
- [ ] `query { employees { employeeId firstName lastName } }` returns all rows
      with only the selected fields
- [ ] `query { employee(id: 5) { firstName lastName position } }` returns David
      Miller; a nonexistent id returns `null`
- [ ] `addEmployee` inserts and returns the new employee with a
      database-generated `employeeId`
- [ ] `updateEmployee` updates and returns the employee; nonexistent id → `null`
- [ ] `deleteEmployee` returns `true` on success, `false` for nonexistent id
- [ ] All four curl examples in README work as pasted
- [ ] The variables example (§8.3) works in GraphiQL
- [ ] `frontend/index.html` performs all five operations against `/graphql`
      from a browser (CORS working)
- [ ] All client-input SQL is parameterized (`?` placeholders) — zero string
      concatenation
- [ ] No excluded feature (§2) is present
- [ ] README commands are exact and complete (all 8 command categories)

---

## 10. Three-Hour Learning Sequence

| Phase | Duration | Content |
|---|---:|---|
| 1 — Database setup | 15 min | Run `create_database.py`, verify rows in SQLite |
| 2 — GraphQL schema | 20 min | Schema, `Employee` type, Query, Mutation, fields, arguments |
| 3 — Query resolvers | 30 min | `employees`, `employee(id)`; exercise in GraphiQL |
| 4 — Mutation resolvers | 40 min | `addEmployee`, `updateEmployee`, `deleteEmployee`; exercise in GraphiQL |
| 5 — curl | 25 min | All four CRUD categories; observe `POST /graphql` uniformity |
| 6 — Apollo Client | 40 min | Build/run `frontend/index.html`; trace Browser → Apollo → GraphQL → resolver → SQLite |
| 7 — Review | 10 min | Schema, type, query, mutation, resolver, argument, variable, endpoint, JSON, Apollo |

---

## 11. Final Conceptual Model (what the learner should retain)

```text
Apollo Client / curl / GraphQL IDE
              |
              | GraphQL
              v
         GraphQL Schema
              |
              v
           Resolver
              |
              | SQL
              v
            SQLite
```

```text
SQL SELECT  ≈ GraphQL Query
SQL INSERT  ≈ GraphQL Mutation
SQL UPDATE  ≈ GraphQL Mutation
SQL DELETE  ≈ GraphQL Mutation
```

The GraphQL server is the semantic API presented to the client; the resolver
is the implementation bridge between the GraphQL schema and the SQLite
datastore.
