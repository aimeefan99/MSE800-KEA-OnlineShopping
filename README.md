# Second-Hand Trading Platform

*With AI One-Click Listing and Smart Homepage Recommendation*

---

## Overview

This project is a web-based second-hand trading platform developed for the **MSE800 Software Engineering** course.

The platform allows users to buy and sell products in a second-hand marketplace, supported by an AI-assisted listing feature for sellers and a smart homepage recommendation feature for buyers. Visitors can browse listings without creating an account, while registered users can create and manage listings, submit purchase requests, save favourite items, complete transactions, and leave reviews. Administrators manage users, listings, and request records to help keep the platform safe and reliable.

The project follows an **Agile software development methodology** and applies object-oriented design principles, UML modelling, and modern software engineering practices throughout development.

---

## Project Objectives

- Develop a secure and user-friendly second-hand trading platform.
- Simplify product listing creation using artificial intelligence.
- Improve homepage product discovery through personalised recommendations.
- Apply Agile software development practices throughout the project lifecycle.
- Demonstrate maintainable, scalable, and well-structured software architecture.

---

## Highlighted Features

### AI One-Click Listing Assistant

Generates a draft product listing from a single uploaded product image using the OpenAI API. The generated draft includes:

- Product title
- Category
- Description
- Suggested price

The user can review and edit the generated information before publishing the listing.

---

### Interest-Based Homepage Recommendation

Displays personalised homepage recommendations by analysing the user's recent interactions, including:

- Recent searches
- Browsing history
- Favourite listings

Instead of showing the same fixed homepage content to every user, the platform prioritises listings that better match each user's recent interests.

---

## Technology Stack

- Backend: Python, Flask
- Frontend: HTML, CSS, Bootstrap
- Database: SQLite
- AI Integration: OpenAI API
- Containerization and Deployment: Docker, Kubernetes
- Version Control: GitHub
- Project Management: Jira
- Design Tool: draw.io

---

## Environment Requirements

- Python 3.8.20
- pip
- Docker
- Kubernetes

---

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
├── utils/
└── README.md
```

### Folder Description

| Folder | Description |
|----------|-------------|
| `routes/` | Flask route handlers grouped by feature |
| `services/` | Business logic and AI services |
| `models/` | Entity classes, factories, and database helpers |
| `templates/` | HTML templates |
| `static/` | CSS, JavaScript, images and uploads |
| `scripts/` | Database initialisation and utility scripts |
| `doc/` | Project documentation |
| `diagram/` | UML diagrams created using draw.io |
| `utils/` | Shared decorators and helper utilities |

---

## Run the Project

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialise the Database

```bash
python3 scripts/init_db.py
```

### 3. Start the Application

```bash
python3 app.py
```

The development server runs at:

```
http://127.0.0.1:5000
```

### 4. Run Code Quality Check

Use `pylint` to check code quality during development:

```bash
pylint app.py routes services models utils
```

---

## Documentation

Project documentation can be found in the `doc/` folder.

- [Project Plan](doc/Project_Plan_Agile_Workflow.md)
- [System Design](doc/System_Design.md)
- [API Specification](doc/API_Specification.md)
- [Development Guidelines](doc/Development_Guidelines.md)

---

## Development Approach

The project follows an Agile development process consisting of multiple sprints.

Development activities include:

- Requirements analysis
- System design
- Database design
- UML modelling
- Backend development
- Frontend development
- AI feature integration
- Testing
- Docker containerisation
- Kubernetes deployment

---

## License

This project was developed for the **MSE800 Software Engineering** course and is intended for educational purposes only.
