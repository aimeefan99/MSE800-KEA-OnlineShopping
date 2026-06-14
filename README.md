# Second-Hand Trading Platform

*With AI One-Click Listing and Interest-Based Homepage Recommendation*

## Overview

This project is a web-based second-hand trading platform developed for `MSE800`.

Visitors can browse listings, search products, apply filters, and view item details before signing in. Registered users can then create listings, save items to a favorite list, submit purchase requests, complete transactions, and use profile features. Administrator functions are included for basic platform management.

## Highlighted Features

- `AI One-Click Listing Assistant`
  - generate a draft listing from one product image
- `Interest-Based Homepage Recommendation`
  - prioritise homepage listings based on recent search, browsing, and favorite list behaviour

## Current Scope

- guest browsing, search, filters, and item detail view
- user registration, login, logout, and profile editing
- listing creation, editing, deletion, and status support
- favorite list support
- purchase request workflow
- ratings, reviews, and trust indicators
- administrator management pages and control actions
- AI-assisted listing draft generation
- lightweight homepage recommendation logic

## Technology Stack

- Python
- Flask
- HTML
- CSS
- Bootstrap
- SQLite
- OpenAI API
- Docker
- Kubernetes

## Environment Requirements

- Python 3.x
- pip
- Docker
- Kubernetes

## Project Structure

```text
project-root/
├── app.py
├── config.py
├── requirements.txt
├── routes/
├── services/
├── models/
├── templates/
├── static/
├── scripts/
├── doc/
├── diagram/
└── README.md
```

- `app.py` - application entry point
- `config.py` - shared configuration values
- `routes/` - Flask route handlers grouped by feature
- `services/` - business logic grouped by feature
- `models/` - database connection and schema code
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, and uploaded files
- `scripts/` - setup and utility scripts
- `doc/` - project documents
- `diagram/` - draw.io diagrams

## Run the Project

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Initialize the database:
   - `python3 scripts/init_db.py`
3. Start the application:
   - `python3 app.py`

The default development server runs at `http://127.0.0.1:5000`.

## Documentation

- [Project Plan](doc/Project_Plan_Agile_Workflow.md)
- [System Design](doc/System_Design.md)
- [API Specification](doc/API_Specification.md)
- [Development Guidelines](doc/Development_Guidelines.md)

