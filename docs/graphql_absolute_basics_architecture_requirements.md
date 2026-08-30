# GraphQL Absolute-Basics Tutorial — Architecture & Technical Requirements

## 1. Purpose

Build a deliberately small GraphQL learning application that can be completed and understood in approximately three hours.

The objective is to learn the core GraphQL execution model:

- GraphQL schema
- GraphQL object types
- GraphQL queries
- GraphQL mutations
- GraphQL resolvers
- GraphQL variables and arguments
- GraphQL JSON responses
- GraphQL over HTTP
- Browser-based GraphQL testing
- `curl`-based GraphQL testing
- Apollo Client calling a GraphQL endpoint

The application must remain intentionally simple. It is a learning exercise, not a production application.

---

## 2. Primary Learning Goal

The learner should understand the following end-to-end execution path:

```text
Browser / Apollo Client / curl
            |
            | GraphQL Query or Mutation
            v
      /graphql endpoint
            |
            v
      GraphQL Server
       (Strawberry)
            |
            v
       Resolver Function
            |
            | SQL
            v
          SQLite
            |
            v
     Employee_Base_0
            |
            v
       Resolver Result
            |
            v
      GraphQL JSON Response
            |
            v
Browser / Apollo Client / curl
```

The key architectural principle is:

> GraphQL resolvers communicate directly with SQLite.

There must be no intermediate REST API layer.

---

# 3. Technology Stack

Use the smallest practical stack.

## 3.1 Backend

- Python 3
- SQLite
- Python built-in `sqlite3` module
- Strawberry GraphQL

Do not use an ORM.

Specifically, do not use:

- SQLAlchemy
- Django ORM
- Prisma
- Peewee

The SQL statements should remain visible inside the resolver implementation so the relationship between GraphQL operations and SQL operations is easy to understand.

---

## 3.2 GraphQL Server

Use Strawberry GraphQL.

The GraphQL server must expose one endpoint:

```text
/graphql
```

The implementation should provide a browser-accessible GraphQL IDE if supported by the selected Strawberry configuration.

The GraphQL endpoint must support HTTP requests from:

- the browser GraphQL IDE
- `curl`
- Apollo Client

---

## 3.3 Frontend

Use a minimal browser-based Apollo Client.

The frontend should be intentionally basic.

It should demonstrate:

- retrieving all employees
- retrieving one employee
- inserting an employee
- updating an employee
- deleting an employee

The frontend does not need professional styling.

The purpose is only to demonstrate GraphQL client/server interaction.

---

# 4. Project Structure

Use a minimal project structure similar to:

```text
graphql_basic/
│
├── employees.db
├── create_database.py
├── graphql_server.py
├── requirements.txt
├── README.md
│
└── frontend/
    └── index.html
```

Additional files may be added only when necessary for clarity.

Avoid unnecessary framework-generated directory structures.

---

# 5. SQLite Database

Create one SQLite database:

```text
employees.db
```

Create one table:

```text
Employee_Base_0
```

---

# 6. Employee_Base_0 Table Definition

The table must contain the following columns:

| Column | SQLite Type | Required |
|---|---|---|
| employee_id | INTEGER PRIMARY KEY AUTOINCREMENT | Yes |
| first_name | TEXT | Yes |
| last_name | TEXT | Yes |
| age | INTEGER | Yes |
| gender | TEXT | Yes |
| position | TEXT | Yes |
| salary | REAL | Yes |
| city | TEXT | Yes |

`employee_id` is required so that individual rows can be retrieved, updated, and deleted unambiguously.

---

# 7. Initial Data

Insert exactly ten sample employee records when the database is created.

Example dataset:

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

The database initialization script should be repeatable.

If the table already exists, the script should either:

1. recreate it cleanly, or
2. detect the existing table and avoid inserting duplicate sample rows.

For an introductory tutorial, recreating the database is acceptable.

---

# 8. GraphQL Employee Type

Define a GraphQL type named:

```text
Employee
```

It should expose:

```text
employeeId
firstName
lastName
age
gender
position
salary
city
```

Prefer GraphQL-style camelCase field names even though SQLite uses snake_case column names.

The tutorial should make this mapping visible and easy to understand.

Example:

```text
SQLite column      GraphQL field

employee_id   ->   employeeId
first_name    ->   firstName
last_name     ->   lastName
```

---

# 9. GraphQL Query Requirements

Implement two basic GraphQL Query operations.

## 9.1 Retrieve All Employees

GraphQL field:

```graphql
employees
```

Conceptual operation:

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

Resolver SQL:

```sql
SELECT *
FROM Employee_Base_0;
```

The client must be able to choose only the fields it wants returned.

This exercise should explicitly demonstrate GraphQL field selection.

---

## 9.2 Retrieve One Employee

GraphQL field:

```graphql
employee(id: Int!)
```

Example:

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

Resolver SQL:

```sql
SELECT *
FROM Employee_Base_0
WHERE employee_id = ?;
```

The resolver must use a parameterized SQL statement.

---

# 10. GraphQL Mutation Requirements

GraphQL uses mutations for create, update, and delete operations.

Implement three mutations.

---

## 10.1 Insert Employee

GraphQL mutation:

```text
addEmployee
```

The mutation should accept:

```text
firstName
lastName
age
gender
position
salary
city
```

The database generates `employee_id`.

Conceptual GraphQL example:

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

Resolver SQL:

```sql
INSERT INTO Employee_Base_0
(
    first_name,
    last_name,
    age,
    gender,
    position,
    salary,
    city
)
VALUES (?, ?, ?, ?, ?, ?, ?);
```

The resolver must return the newly created employee.

---

# 11. Update Employee

GraphQL mutation:

```text
updateEmployee
```

The mutation must identify the employee using:

```text
employeeId
```

For the absolute-basic tutorial, it is acceptable for the mutation to require all employee fields rather than implementing sophisticated partial-update semantics.

Example:

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

Resolver SQL:

```sql
UPDATE Employee_Base_0
SET
    first_name = ?,
    last_name = ?,
    age = ?,
    gender = ?,
    position = ?,
    salary = ?,
    city = ?
WHERE employee_id = ?;
```

The mutation should return the updated employee.

---

# 12. Delete Employee

GraphQL mutation:

```text
deleteEmployee
```

Example:

```graphql
mutation {
  deleteEmployee(employeeId: 10)
}
```

Resolver SQL:

```sql
DELETE FROM Employee_Base_0
WHERE employee_id = ?;
```

The mutation may return either:

```text
Boolean
```

or a simple result object.

For maximum simplicity, prefer:

```graphql
Boolean
```

Example response:

```json
{
  "data": {
    "deleteEmployee": true
  }
}
```

---

# 13. Required GraphQL Schema Shape

The final schema should conceptually resemble:

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

Exact Strawberry syntax may differ.

The logical GraphQL interface should remain equivalent to this definition.

---

# 14. Resolver Design

Resolvers must be simple Python functions.

Each resolver should visibly perform these steps:

```text
1. open SQLite connection
2. execute parameterized SQL
3. obtain row or rows
4. convert SQLite result to Employee object
5. close connection
6. return result
```

Example conceptual resolver:

```python
def get_employee(id):
    connection = sqlite3.connect("employees.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM Employee_Base_0 WHERE employee_id = ?",
        (id,)
    )

    row = cursor.fetchone()

    connection.close()

    return row
```

The actual implementation should convert the database row to the Strawberry `Employee` type.

The tutorial should prioritize readability over abstraction.

Do not introduce:

- repository classes
- service classes
- dependency injection
- DAO layers
- generic database abstractions

---

# 15. GraphQL-to-SQL Mapping

The tutorial must explicitly demonstrate this mapping:

| GraphQL Operation | Resolver | SQL |
|---|---|---|
| `employees` | `get_employees()` | `SELECT` |
| `employee(id)` | `get_employee()` | `SELECT ... WHERE` |
| `addEmployee(...)` | `add_employee()` | `INSERT` |
| `updateEmployee(...)` | `update_employee()` | `UPDATE` |
| `deleteEmployee(...)` | `delete_employee()` | `DELETE` |

This mapping is a primary instructional objective.

---

# 16. GraphQL Browser IDE Exercises

Before building the Apollo Client frontend, exercise the GraphQL endpoint using the browser-based GraphQL IDE.

Perform these five operations:

```text
1. Query all employees
2. Query one employee
3. Add one employee
4. Update one employee
5. Delete one employee
```

The learner should inspect both:

```text
GraphQL request
```

and:

```text
JSON response
```

for every operation.

---

# 17. curl Requirements

Provide working `curl` examples for four CRUD categories.

All GraphQL requests should use the same HTTP endpoint:

```text
http://localhost:<PORT>/graphql
```

Use the actual port selected by the implementation.

---

## 17.1 SELECT / Query

Provide a command that retrieves employees.

Example GraphQL payload:

```graphql
query {
  employees {
    employeeId
    firstName
    lastName
    position
    salary
    city
  }
}
```

---

## 17.2 INSERT / Mutation

Provide a `curl` command that invokes:

```text
addEmployee
```

---

## 17.3 UPDATE / Mutation

Provide a `curl` command that invokes:

```text
updateEmployee
```

---

## 17.4 DELETE / Mutation

Provide a `curl` command that invokes:

```text
deleteEmployee
```

---

# 18. GraphQL Variables

After demonstrating literal values directly inside GraphQL operations, include one simple example using GraphQL variables.

Example:

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

Variables:

```json
{
  "id": 5
}
```

Do not introduce more sophisticated variable or input-object patterns until the basic literal form is understood.

---

# 19. Apollo Client Requirements

Build a minimal browser frontend that uses Apollo Client.

It must connect to:

```text
/graphql
```

The frontend should demonstrate the following operations.

---

## 19.1 List Employees

Display at least:

```text
employeeId
firstName
lastName
position
city
```

---

## 19.2 Retrieve One Employee

Allow an employee ID to be entered.

Execute the GraphQL:

```text
employee(id)
```

query.

Display the returned employee.

---

## 19.3 Insert Employee

Provide a minimal form for:

```text
firstName
lastName
age
gender
position
salary
city
```

Submit using:

```text
addEmployee
```

---

## 19.4 Update Employee

Provide a minimal mechanism to invoke:

```text
updateEmployee
```

The interface does not need sophisticated editing behavior.

A simple form is sufficient.

---

## 19.5 Delete Employee

Allow an employee ID to be supplied and execute:

```text
deleteEmployee
```

---

# 20. Apollo Client Learning Objective

The learner should be able to recognize this flow:

```text
JavaScript / Apollo Client
          |
          | gql`
          |   query {...}
          | `
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

Apollo Client must not hide the GraphQL query text from the learner.

The tutorial should show the actual `gql` query or mutation used by Apollo.

---

# 21. Error Handling

Keep error handling minimal.

The application should handle these basic cases:

### Employee does not exist

For:

```text
employee(id)
```

return:

```text
null
```

or a simple GraphQL error.

### Update nonexistent employee

Return:

```text
null
```

or a simple GraphQL error.

### Delete nonexistent employee

Return:

```text
false
```

### Invalid GraphQL syntax

Allow the GraphQL server to return the normal GraphQL error structure.

Do not build a custom enterprise error framework.

---

# 22. Parameterized SQL

All SQL operations that accept client input must use SQLite parameter substitution.

Correct:

```python
cursor.execute(
    "SELECT * FROM Employee_Base_0 WHERE employee_id = ?",
    (employee_id,)
)
```

Do not construct SQL using string concatenation.

Incorrect:

```python
cursor.execute(
    "SELECT * FROM Employee_Base_0 WHERE employee_id = " + employee_id
)
```

This requirement introduces basic SQL injection awareness without expanding the tutorial into a security course.

---

# 23. Deliberately Excluded Features

Do not implement the following in this tutorial:

- REST APIs
- FastAPI CRUD endpoints
- authentication
- authorization
- JWT
- OAuth
- role-based access control
- ORM
- SQLAlchemy
- PostgreSQL
- MySQL
- Redis
- Kafka
- Docker
- Kubernetes
- GraphQL subscriptions
- WebSockets
- GraphQL federation
- DataLoader
- batching
- advanced caching
- pagination
- sorting
- complex filtering
- interfaces
- unions
- fragments as a major topic
- microservices
- gateway architecture
- production deployment
- enterprise logging
- extensive automated tests
- CI/CD

These subjects can be introduced after the basic GraphQL data path is understood.

---

# 24. Expected Runtime Architecture

The completed tutorial should have approximately this architecture:

```text
+------------------------------------------------------------+
|                    Browser                                 |
|                                                            |
|  +------------------+       +----------------------------+ |
|  | GraphQL IDE      |       | Apollo Client HTML/JS      | |
|  +--------+---------+       +-------------+--------------+ |
|           |                               |                |
+-----------|-------------------------------|----------------+
            |                               |
            | GraphQL over HTTP             |
            +---------------+---------------+
                            |
                            v
                  +--------------------+
                  | Strawberry GraphQL |
                  |                    |
                  | /graphql           |
                  +---------+----------+
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
          Query         Mutation        Resolver
                                        Functions
                                           |
                                           |
                                           v
                                   +---------------+
                                   | Python sqlite3|
                                   +-------+-------+
                                           |
                                           | SQL
                                           v
                                   +---------------+
                                   | employees.db  |
                                   |               |
                                   |Employee_Base_0|
                                   +---------------+
```

---

# 25. Three-Hour Learning Sequence

Use this approximate progression.

## Phase 1 — Database Setup

Approximate duration:

```text
15 minutes
```

Tasks:

- create `employees.db`
- create `Employee_Base_0`
- insert ten rows
- verify rows using SQLite

No database concepts need to be taught beyond what is necessary to run the lab.

---

## Phase 2 — GraphQL Schema

Approximate duration:

```text
20 minutes
```

Explain:

- GraphQL schema
- `Employee` type
- `Query`
- `Mutation`
- fields
- arguments

---

## Phase 3 — GraphQL Query Resolvers

Approximate duration:

```text
30 minutes
```

Implement:

```text
employees
employee(id)
```

Exercise them through the GraphQL browser IDE.

---

## Phase 4 — GraphQL Mutation Resolvers

Approximate duration:

```text
40 minutes
```

Implement:

```text
addEmployee
updateEmployee
deleteEmployee
```

Exercise each through the browser GraphQL IDE.

---

## Phase 5 — curl

Approximate duration:

```text
25 minutes
```

Exercise:

```text
Query
INSERT Mutation
UPDATE Mutation
DELETE Mutation
```

Observe that every operation uses:

```text
POST /graphql
```

while the GraphQL document determines the operation.

---

## Phase 6 — Apollo Client

Approximate duration:

```text
40 minutes
```

Implement the minimal browser frontend.

Exercise:

```text
Browser
   ↓
Apollo Client
   ↓
GraphQL
   ↓
Resolver
   ↓
SQLite
```

---

## Phase 7 — Review

Approximate duration:

```text
10 minutes
```

Confirm understanding of:

```text
Schema
Type
Query
Mutation
Resolver
Argument
Variable
GraphQL endpoint
JSON response
Apollo Client
```

---

# 26. Required Deliverables

Claude Code should generate the following working artifacts.

## Deliverable 1

```text
create_database.py
```

Responsibilities:

- create SQLite database
- create `Employee_Base_0`
- insert ten records

---

## Deliverable 2

```text
graphql_server.py
```

Responsibilities:

- define GraphQL `Employee`
- define `Query`
- define `Mutation`
- define resolvers
- connect resolvers directly to SQLite
- expose `/graphql`

---

## Deliverable 3

```text
requirements.txt
```

Contain only necessary Python dependencies.

Do not add unnecessary packages.

---

## Deliverable 4

```text
frontend/index.html
```

Minimal browser-based Apollo Client.

Must demonstrate:

- SELECT/query
- INSERT mutation
- UPDATE mutation
- DELETE mutation

---

## Deliverable 5

```text
README.md
```

The README must provide exact commands for:

1. creating the Python environment
2. installing dependencies
3. creating the database
4. starting the GraphQL server
5. opening the GraphQL browser IDE
6. running each GraphQL example
7. executing each `curl` example
8. opening/running the Apollo Client frontend

---

# 27. Tutorial Documentation Requirement

Comments and README explanations should repeatedly connect the software implementation to the conceptual flow.

For example:

```text
GraphQL:

employee(id: 5)

        ↓

Resolver:

get_employee(5)

        ↓

SQL:

SELECT *
FROM Employee_Base_0
WHERE employee_id = 5

        ↓

SQLite row

        ↓

Employee GraphQL object

        ↓

JSON response
```

The implementation should make this relationship obvious.

---

# 28. Definition of Done

The tutorial is complete when the learner can perform all of the following.

### Read all rows

```graphql
query {
  employees {
    employeeId
    firstName
    lastName
  }
}
```

### Read one row

```graphql
query {
  employee(id: 5) {
    firstName
    lastName
    position
  }
}
```

### Insert one row

Using:

```text
addEmployee
```

### Update one row

Using:

```text
updateEmployee
```

### Delete one row

Using:

```text
deleteEmployee
```

### Repeat the CRUD operations using curl

The learner must be able to see the GraphQL request body.

### Retrieve data using Apollo Client

The learner must be able to identify the Apollo `gql` statement responsible for the request.

---

# 29. Final Conceptual Model

At the end of the tutorial, the learner should be able to explain the system as:

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

And should understand:

```text
SQL SELECT  ≈ GraphQL Query

SQL INSERT  ≈ GraphQL Mutation
SQL UPDATE  ≈ GraphQL Mutation
SQL DELETE  ≈ GraphQL Mutation
```

The GraphQL server is therefore the semantic API presented to the client, while the resolver is the implementation bridge between the GraphQL schema and the SQLite datastore.

---

# 30. Implementation Philosophy

When generating the tutorial code, optimize for:

```text
clarity > abstraction
visibility > framework magic
small code > production architecture
direct SQL > ORM
one endpoint > multiple API layers
learning GraphQL > building infrastructure
```

The completed system should be small enough that a learner can trace one GraphQL operation from the browser all the way to the SQLite SQL statement without navigating through multiple abstraction layers.
