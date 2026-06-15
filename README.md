# AI-Powered Second-Hand Trading Platform

*With AI One-Click Listing Assistant and Interest-Based Homepage Recommendation*

---

## Overview

This project is an AI-powered web-based second-hand trading platform developed for the **MSE800 Software Engineering** course.

The platform enables users to buy and sell second-hand products through an intuitive marketplace while incorporating artificial intelligence to improve both the selling and browsing experience. Visitors can browse listings without creating an account, while registered users can create and manage listings, submit purchase requests, save favourite items, complete transactions, and leave reviews. Administrators are responsible for managing users, listings, and platform activities to maintain a safe and reliable marketplace.

The project follows an **Agile software development methodology** and applies object-oriented design principles, UML modelling, and modern software engineering practices throughout development.

---

## Team

| Team Member | Primary Responsibility |
|-------------|------------------------|
| Member 1 | System Design, Interest-Based Homepage Recommendation, Frontend & Backend Development |
| Member 2 | User Stories, Sprint Planning, AI One-Click Listing Assistant, Frontend & Backend Development |

> Although each member leads one highlighted AI feature, **both team members contribute to both frontend and backend development throughout the project.**

---

## Project Objectives

- Develop a secure and user-friendly second-hand trading platform.
- Simplify product listing creation using artificial intelligence.
- Improve homepage product discovery through personalised recommendations.
- Apply Agile software development practices throughout the project lifecycle.
- Demonstrate maintainable, scalable, and well-structured software architecture.

---

## Highlighted AI Features

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

Instead of displaying identical homepage content for every user, the platform prioritises listings that match each user's recent interests.

---

## Current Scope

### Visitor Features

- Browse listings
- Search listings
- Apply filters
- View listing details
- View public profiles
- Register
- Log in

### User Features

- Edit profile
- Create listings
- Edit and delete own listings
- Generate listings using AI
- Save and manage favourite listings
- Submit purchase requests
- Accept or reject purchase requests
- Confirm completed transactions
- View transaction history
- Leave ratings and reviews
- View personalised homepage recommendations

### Administrator Features

- Manage user accounts
- Manage listings
- Remove inappropriate listings
- View purchase requests
- View completed transactions
- Lock user accounts
- Lock purchase requests

---

## Technology Stack

### Backend

- Python
- Flask
- SQLite

### Frontend

- HTML
- CSS
- Bootstrap
- JavaScript

### AI

- OpenAI API

### Deployment

- Docker
- Kubernetes

### Version Control

- Git
- GitHub

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
└── README.md
```

### Folder Description

| Folder | Description |
|----------|-------------|
| `routes/` | Flask route handlers grouped by feature |
| `services/` | Business logic and AI services |
| `models/` | Database models and schema |
| `templates/` | HTML templates |
| `static/` | CSS, JavaScript, images and uploads |
| `scripts/` | Database initialisation and utility scripts |
| `doc/` | Project documentation |
| `diagram/` | UML diagrams created using draw.io |

---

## UML Diagrams

The project design is documented using UML diagrams before implementation.

Completed diagrams include:

- ✅ Use Case Diagram
- ✅ Entity Relationship (ER) Diagram
- ✅ Class Diagram

Remaining diagrams:

- ⏳ Activity Diagram
- ⏳ System Architecture Diagram

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

---

## Documentation

Project documentation can be found in the `doc/` folder.

- Project Proposal
- Agile Workflow
- Sprint Planning
- Product Backlog
- System Design
- API Specification
- Development Guidelines

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

## Repository Status

**Current Status:** 🚧 In Development

Completed:

- ✅ Project Planning
- ✅ Agile Workflow
- ✅ User Stories
- ✅ Sprint Planning
- ✅ System Design
- ✅ Database Design
- ✅ Use Case Diagram
- ✅ ER Diagram
- ✅ Class Diagram

In Progress:

- 🚧 Backend Development
- 🚧 Frontend Development
- 🚧 AI Feature Integration

Upcoming:

- ⏳ Activity Diagram
- ⏳ System Architecture Diagram
- ⏳ Testing
- ⏳ Docker Deployment
- ⏳ Kubernetes Deployment

---

## License

This project was developed for the **MSE800 Software Engineering** course and is intended for educational purposes only.