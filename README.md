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
- AI Integration: Gemini API
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

Create a local environment file before running the project:

```bash
cp .env.example .env
```

Then update any values you need, especially the secret key and AI API key.

For local browser access and Docker runs, keep `APP_PORT=5001`. The default
example file uses `APP_HOST=0.0.0.0`, which works for container access and also
still allows you to open the site in the browser with `http://127.0.0.1:5001`.

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

By default, the development server runs at:

```
http://127.0.0.1:5001
```

Key runtime settings are now managed outside hard-coded source files through environment
variables, including:

- `SECRET_KEY`
- `DATABASE_PATH`
- `UPLOAD_FOLDER`
- `IMAGE_STORAGE_PROVIDER`
- `S3_BUCKET_NAME`
- `S3_REGION`
- `S3_PUBLIC_BASE_URL`
- `APP_HOST`
- `APP_PORT`
- `GEMINI_API_KEY`

When `IMAGE_STORAGE_PROVIDER=s3`, listing images are uploaded to Amazon S3 and
listing records should store the S3 object key rather than a local `uploads/...`
path.

### 4. Run Code Quality Check

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

### 3. Open the app

Once the container starts successfully, open:

```text
http://127.0.0.1:5001
```

Notes:

- the container installs Python dependencies from `requirements.txt`
- the startup command automatically initializes the SQLite schema before launching Flask
- the container runs the app on `0.0.0.0:5001` so the browser can access it from the host machine

### S3 image storage

For deployment, configure the following values in `.env`:

```bash
IMAGE_STORAGE_PROVIDER=s3
S3_BUCKET_NAME=mse800-market-images
S3_REGION=us-east-1
S3_PUBLIC_BASE_URL=https://mse800-market-images.s3.us-east-1.amazonaws.com
```

If you have already uploaded legacy listing images from `instance/uploads` into
the bucket using their original filenames, run the migration script once to
update database image references from `uploads/filename.jpg` to `filename.jpg`:

```bash
python scripts/migrate_listing_images_to_s3_keys.py
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
