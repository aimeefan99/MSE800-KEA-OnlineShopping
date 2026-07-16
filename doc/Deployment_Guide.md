# Deployment Guide

## 1. Purpose

This document explains how the `Second-Hand Trading Platform - Kea Marketplace`
is deployed and updated.

It reflects the current project deployment approach:

- the Flask application runs in Docker
- the Docker container is hosted on AWS EC2
- the SQLite database is persisted on the EC2 host
- listing images are stored in Amazon S3
- runtime configuration is provided through environment variables
- deployment automation is handled through GitHub Actions

## 2. Current Deployment Architecture

The deployed system uses these main parts:

- `AWS EC2` as the application host
- `Docker` to package and run the Flask application
- `docker compose` on the EC2 host to recreate the running container
- `SQLite` for prototype data persistence
- `Amazon S3` for listing image storage
- `Google Gemini API` for AI listing draft generation

In the current deployment:

- the application container listens on port `5001`
- the EC2 host exposes the app publicly on port `80`
- the deployed site is currently accessed through the Elastic IP
- a local host-mapped domain may also be used during demonstration

## 3. EC2 Runtime Layout

The application is deployed on an EC2 instance under a directory similar to:

```text
/home/ubuntu/mse800-deploy
```

That deployment directory contains:

- the deployment-side `.env` file
- the `docker-compose.yml` file
- a bind-mounted database folder such as `./flask_db`

The database volume is mounted into the container as:

```text
/app/instance
```

This allows the SQLite database file to survive container recreation.

## 4. Docker Compose Deployment

The deployed container is recreated through the Docker Compose plugin command:

```bash
docker compose up -d --force-recreate
```

This is the command currently used on the EC2 host after application updates.

The deployment-side `docker-compose.yml` follows this pattern:

```yaml
services:
  web:
    image: mse800-2
    ports:
      - "80:5001"
    volumes:
      - ./flask_db:/app/instance
    env_file:
      - .env
```

Notes:

- port `80` on the EC2 host is mapped to port `5001` in the container
- the SQLite database stays on the EC2 host through the bind-mounted volume
- the container reads runtime variables from the deployment `.env` file
- `docker compose` is used through the Docker plugin, not the old `docker-compose` command

## 5. Environment Configuration

Runtime configuration is not hard-coded in source files. It is provided through
the deployment `.env` file.

Typical deployment variables include:

- `SECRET_KEY`
- `DATABASE_PATH`
- `APP_HOST`
- `APP_PORT`
- `FLASK_DEBUG`
- `S3_BUCKET_NAME`
- `S3_REGION`
- `S3_PUBLIC_BASE_URL`
- `AI_PROVIDER`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `GEMINI_FALLBACK_MODEL`
- `AI_REQUEST_TIMEOUT_SECONDS`
- `AI_IMAGE_MAX_DIMENSION`

These values must be set correctly on the EC2 host before starting the container.

## 6. Database Persistence

The deployed system still uses `SQLite`.

In this project, the SQLite database file is not stored only inside the container.
Instead, it is persisted on the EC2 host and mounted into the container through
Docker volume binding.

This means:

- container recreation does not delete the database automatically
- user accounts, listings, requests, reviews, and favorites remain available
- the deployment remains suitable for a prototype or small single-host system

Current limitation:

- SQLite is still a single-host database
- this deployment is not designed for multi-instance scaling

## 7. Image Storage with Amazon S3

Listing images in the deployed environment are stored in `Amazon S3`.

The application stores the image reference in the database and resolves it to a
public S3 URL when rendering listing pages.

This means:

- listing images do not depend on the container filesystem
- images remain available after container recreation
- deployed image storage is separated from application runtime storage

This also requires:

- the target S3 bucket to exist
- the bucket policy or object permissions to allow image access as required
- the deployment environment to provide valid AWS access through the EC2 instance role
  or another approved AWS credential mechanism

## 8. Deployed Access

The deployed application is currently accessed through:

- public Elastic IP: `http://3.227.125.114/`
- local host-mapped domain used during demonstration: `http://kea-marketplace.com/`

The `kea-marketplace.com` address is currently a local host mapping rather than
a public DNS domain.

## 9. EC2 Update Commands

The EC2 host can still be updated directly when troubleshooting or verifying
deployment commands:

```bash
cd /home/ubuntu/mse800-deploy
git pull
docker build -t mse800-2 .
docker compose up -d --force-recreate
```

This updates the code, rebuilds the Docker image, and recreates the running
application container.

## 10. GitHub Actions Deployment Workflow

The deployment automation workflow uses `GitHub Actions`.

The workflow is:

1. application code is pushed to GitHub
2. GitHub Actions runs a deployment workflow
3. the workflow connects to the EC2 host through SSH
4. the workflow updates the project code on the EC2 host
5. the workflow rebuilds the Docker image
6. the workflow runs `docker compose up -d --force-recreate`

This workflow fits the current project because:

- the source code is already hosted on GitHub
- the deployed app already runs through Docker on a single EC2 host
- deployment can be automated without introducing a more complex platform

## 11. Security Notes

In the deployed system, we use these security practices:

- we keep sensitive runtime values out of source control
- we keep the deployment `.env` file on the EC2 host instead of committing it to the repository
- we do not store SSH private keys in the repository
- we use GitHub Actions secrets for deployment credentials
- we use AWS access that is limited to the deployment and S3 image-storage needs of the project
- we use AWS IAM-based access for S3 instead of storing long-term cloud credentials in source code
- we keep application code, runtime secrets, database storage, and image storage separated across GitHub, EC2, and Amazon S3

## 12. Scope Boundary

This deployment is appropriate for the current project scope and demonstration,
but it is still a lightweight prototype deployment.

It does not currently include:

- a production-managed relational database such as Amazon RDS
- load balancing across multiple instances
- container orchestration such as Kubernetes or Amazon ECS
- a public DNS-managed production domain
- HTTPS certificate management

These items are possible future improvements, but they are outside the current
project scope.
