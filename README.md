# Second-Hand Trading Platform - Kea Marketplace

*With AI One-Click Listing and Smart Homepage Recommendation*

---

## Overview

This project is a web-based second-hand trading platform built to support second-hand buying and selling in a practical marketplace setting.

The platform allows users to buy and sell products in a second-hand marketplace, supported by an AI-assisted listing feature for sellers and a smart homepage recommendation feature for buyers. Visitors can browse listings without creating an account, while registered users can create and manage listings, submit purchase requests, save favourite items, complete transactions, and leave reviews. Administrators manage users, listings, and request records to help keep the platform safe and reliable.

The project follows an **Agile software development methodology** and applies object-oriented design principles, UML modelling, and modern software engineering practices throughout development.

The current implemented deployment runs the Flask application in Docker on AWS EC2, uses SQLite for prototype data persistence, stores listing images in Amazon S3, and connects the AI listing assistant to the Google Gemini API.

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

Generates a draft product listing from a single uploaded product image using the Gemini API. The generated draft includes:

- Product title
- Category
- Description

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
- AI Integration: Google Gemini API
- Containerization: Docker
- CI/CD: GitHub Actions
- Cloud Hosting: AWS EC2
- Cloud Image Storage: Amazon S3
- Version Control: GitHub
- Project Management: Jira
- Design Tool: draw.io

---

## Environment Requirements

### Local Development

- Python 3.8+
- pip

### Optional Local Container Run

- Docker

### Deployment Environment

- AWS account
- AWS EC2 instance
- Amazon S3 bucket for listing images
- Google Gemini API key for the AI listing feature

---

## Project Structure

```text
project-root/
├── .env.example
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
| `static/` | CSS, JavaScript, logo, and shared image assets |
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

Create a local environment file before running the project:

```bash
cp .env.example .env
```

Then update any values you need, especially the secret key and AI API key.

For deployed environments, the same runtime configuration can be provided through
an environment file on the EC2 host.

For local browser access and Docker runs, keep `APP_PORT=5001`. The default
example file uses `APP_HOST=0.0.0.0`, which works for container access while
still allowing local browser access through `http://127.0.0.1:5001`.

You can also set environment variables directly in the shell if preferred. For example:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

### 2. Initialise the Database

```bash
python scripts/init_db.py
```

### 3. Start the Application

```bash
python app.py
```

By default, the local development server runs at:

```
http://127.0.0.1:5001
```

Key runtime settings are now managed outside hard-coded source files through environment
variables, including:

- `SECRET_KEY`
- `DATABASE_PATH`
- `UPLOAD_FOLDER`
- `APP_HOST`
- `APP_PORT`
- `S3_BUCKET_NAME`
- `S3_REGION`
- `S3_PUBLIC_BASE_URL`
- `GEMINI_API_KEY`

### 4. Run Smoke Tests

Run the smoke test suite:

```bash
python -m unittest tests.test_smoke
```

### 5. Optional Code Quality Check

Use `pylint` to check code quality during development:

```bash
pylint app.py routes services models utils
```

---

## Run with Docker

### 1. Build the image

```bash
docker build -t mse800-2 .
```

### 2. Start the container

```bash
docker run --rm -p 5001:5001 --env-file .env mse800-2
```

If you do not want to use a local `.env` file, you can pass values directly:

```bash
docker run --rm -p 5001:5001 -e SECRET_KEY=dev-secret-key -e APP_HOST=0.0.0.0 mse800-2
```

### 3. Open the local container app

Once the container starts successfully, open:

```text
http://127.0.0.1:5001
```

Notes:

- the container installs Python dependencies from `requirements.txt`
- the startup command automatically initializes the SQLite schema before launching Flask
- the container runs the app on `0.0.0.0:5001` so the browser can access it from the host machine
- if you want the deployed-style image workflow to work, the runtime environment must also provide the required S3 settings
- if you want the AI listing draft feature to work, the runtime environment must provide a valid `GEMINI_API_KEY`

## Deployment Summary

The current deployment approach uses:

- Docker to package and run the Flask application
- AWS EC2 to host the running container
- Docker Compose on the EC2 host to recreate and restart the containerized app
- SQLite persisted on the EC2 host for prototype data storage
- Amazon S3 to store listing images in the deployed environment
- environment variables to manage runtime configuration and secrets outside source code

In the deployed environment, the application is currently managed with the Docker
Compose plugin command:

```bash
docker compose up -d --force-recreate
```

This is the command used on the EC2 host after updating the deployment files or
pulling new application code.

## CI/CD Workflow

The project uses GitHub Actions to automate deployment updates to AWS EC2.

The implemented workflow is:

- application code is pushed to GitHub
- GitHub Actions runs the deployment workflow
- the workflow connects to the EC2 host over SSH
- the project code on the EC2 host is updated
- the Docker image is rebuilt
- Docker Compose recreates the running application container

This keeps deployment steps more consistent than a fully manual update process
and matches the container-based deployment approach used in the project.

## Deployed Access

The current deployed application is hosted on AWS EC2 and can be accessed through:

- public Elastic IP: `http://3.227.125.114/`
- local host-mapped domain used in development and demonstration: `http://kea-marketplace.com/`

The `kea-marketplace.com` address is currently a local host mapping rather than a public DNS domain.

---

## Documentation

Project documentation can be found in the `doc/` folder.

- [Project Requirements](doc/Project_Requirements.md)
- [Project Plan](doc/Project_Plan_Agile_Workflow.md)
- [System Design](doc/System_Design.md)
- [API Specification](doc/API_Specification.md)
- [Flask Usage](doc/Flask_Usage.md)
- [Feasibility Study](doc/Feasibility_Study.md)
- [System Testing and Quality Assurance](doc/System_Testing_and_Quality_Assurance.md)
- [Maori Principles and Data Sovereignty](doc/Maori_Principles_and_Data_Sovereignty.md)
- [Development Guidelines](doc/Development_Guidelines.md)
- [Deployment Guide](doc/Deployment_Guide.md)

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
- AWS EC2 deployment
- Amazon S3 image storage integration

---

## License

This project was built as a prototype marketplace system for demonstration, testing, and iterative improvement.
