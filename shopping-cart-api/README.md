# Shopping Cart API

A REST API for a shopping cart / shopper system, built with Express and a serverless Postgres database (Neon). Coursework project demonstrating backend API design, parameterized SQL queries, and cloud-database integration.

## What it does

- Exposes CRUD-style endpoints for `shoppers` (create, list) backed by Postgres
- Uses Neon's serverless driver with tagged-template SQL (`sql\`...\``), which parameterizes queries automatically and protects against SQL injection
- Loads database credentials from environment variables via `dotenv`
- Ships a Postman collection (`shopper-app-sql.postman_collection.json`) for exercising the API, and a `resetDB.sql` script to reset schema/seed data

## Tech

Node.js, Express 5, PostgreSQL (Neon serverless), Postman

## Setup

```bash
npm install
# create a .env file with DATABASE_URL=<your neon postgres connection string>
node app.js
```

## Status

Core shopper endpoints implemented and working against a live Neon database.
