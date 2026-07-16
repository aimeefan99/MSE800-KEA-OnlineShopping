# System Design

### Second-Hand Trading Platform - Kea Marketplace

*With AI One-Click Listing and Interest-Based Homepage Recommendation*

## System Scope

This system includes:

- guest browsing of listings and item details
- user registration and login
- user and administrator roles
- account profile viewing and editing
- account-based listing management for signed-in sellers
- listing creation, editing, deletion, and sold status update
- purchase request workflow
- request and transaction history
- profile editing and public profile viewing
- preferred contact method support
- favorite list support
- ratings, reviews, and trust indicators
- AI one-click listing draft generation
- interest-based homepage recommendation
- administrator control actions

## Data Model

### 1. users

Fields:

- `id` - primary key
- `display_name` - public profile name
- `full_name` - user full name
- `date_of_birth` - used for age verification during registration
- `email` - login email
- `phone_number` - optional contact phone
- `preferred_contact_method` - `email` or `phone`
- `password_hash` - encrypted password value
- `role` - `user` or `admin`
- `is_locked` - account lock flag
- `bio` - optional short profile text
- `created_at` - account creation timestamp

Rules:

- `email` must be unique
- one account can act as both buyer and seller in different transactions

### 2. categories

Fields:

- `id` - primary key
- `name` - category name

Rules:

- each listing belongs to one category

### 3. listings

Fields:

- `id` - primary key
- `seller_id` - foreign key to `users.id`
- `category_id` - foreign key to `categories.id`
- `image_url` - single listing image reference stored as an S3 object key
- `title` - listing title
- `description` - listing description
- `condition` - `new` or `used`
- `price` - listing price
- `status` - `available`, `pending`, or `sold`
- `created_at` - creation timestamp
- `updated_at` - last update timestamp

Rules:

- the first version supports one image per listing
- AI category output must be mapped to a valid `category_id` before saving

### 4. requests

Fields:

- `id` - primary key
- `listing_id` - foreign key to `listings.id`
- `buyer_id` - foreign key to `users.id`
- `seller_id` - foreign key to `users.id`
- `status` - `pending`, `accepted`, `rejected`, or `completed`
- `is_locked` - transaction lock flag
- `message` - optional buyer message
- `created_at` - creation timestamp
- `updated_at` - last update timestamp

Rules:

- this table stores both request flow and transaction completion state
- the first version does not use a separate `transactions` table

### 5. reviews

Fields:

- `id` - primary key
- `request_id` - foreign key to `requests.id`
- `reviewer_id` - foreign key to `users.id`
- `reviewed_user_id` - foreign key to `users.id`
- `score` - integer rating from `1` to `5`
- `comment` - optional short review comment
- `created_at` - creation timestamp

Rules:

- each side can review the other once after a completed transaction
- one review record is allowed per `request_id + reviewer_id + reviewed_user_id` combination

### 6. favorite_list

Fields:

- `id` - primary key
- `user_id` - foreign key to `users.id`
- `listing_id` - foreign key to `listings.id`
- `created_at` - save timestamp

Rules:

- each record stores one saved listing for one user
- one user can save one listing only once

## Relationship Summary

- `users.id` -> `listings.seller_id`
- `categories.id` -> `listings.category_id`
- `listings.id` -> `requests.listing_id`
- `users.id` -> `requests.buyer_id`
- `users.id` -> `requests.seller_id`
- `users.id` -> `favorite_list.user_id`
- `listings.id` -> `favorite_list.listing_id`
- `requests.id` -> `reviews.request_id`
- `users.id` -> `reviews.reviewer_id`
- `users.id` -> `reviews.reviewed_user_id`

## Business Rules

- a user email must be unique
- visitors can browse available listings, search, filter, and view item details without registering
- login is required for creating listings, saving favorites, submitting requests, leaving reviews, and all administrator actions
- users must be 18 or older to register
- only completed transactions can be reviewed
- one user leaves one review for the other party per completed request at most
- only the seller of a listing can edit, delete, or mark it as sold
- listing status follows `available -> pending -> sold`
- listings marked as `sold` do not appear in normal browse and search results
- request status follows `pending -> accepted/rejected -> completed`
- a user cannot submit a purchase request on their own listing
- a listing can receive multiple requests, but only one request can be accepted and completed as the final transaction
- `favorite_list` enforces a unique `user_id + listing_id` pair
- `reviews` enforces a unique `request_id + reviewer_id + reviewed_user_id` combination
- when a seller accepts a request, the related listing changes to `pending`
- when a listing is confirmed as sold, remaining open requests for that listing are closed or rejected
- the buyer confirms transaction completion through the platform
- when a transaction is completed, the related listing moves to `sold`
- administrators can view accounts, view listings, view request records, delete inappropriate listings, lock or unlock user accounts, and lock or unlock request records, but they do not decide transaction outcomes for buyers and sellers
- reviews are optional and are never created automatically
- public profiles display trust indicators and the preferred contact method

## Public Profile Data

- display name
- completed transaction count
- average rating or positive feedback rate
- review summary
- preferred contact method
- phone number or email based on the selected contact preference
- short bio if provided

## AI One-Click Listing Assistant

### Flow

1. The seller uploads one product image.
2. The system sends the image to the AI service.
3. The AI service returns a structured draft with a suggested title, suggested category, suggested description, visible text, detected attributes, and confidence.
4. The seller reviews and edits the draft before publishing.

### Output

- suggested title
- suggested category
- suggested description
- visible text
- detected attributes
- confidence level

### Boundaries

- the assistant generates a draft, not a final published listing
- the seller must review and confirm the result
- the result must be based on visible image evidence only
- the first version uses one image only
- the first version does not use external market price data

## Homepage Recommendation Support

### Signals

- recent browsing category ids
- category ids inferred from search behaviour
- favorite list categories

### Recommendation Rule

- the homepage prioritises available listings from the user's recent interest categories
- if not enough matching listings exist, the homepage falls back to recent available listings
- when the user is logged in, their own listings are excluded from homepage recommendations

### Boundaries

- the first version uses lightweight rule-based logic
- the first version does not use a heavy recommendation engine, vector database, or complex machine learning pipeline

## System Architecture Diagram Design

### Main Components

- User Browser
- Flask Web Application
- HTML Templates and Bootstrap UI
- Application Services
- SQLite Database
- Amazon S3 Bucket
- Google Gemini API
- Docker Container on AWS EC2

### Main Connections

- the user accesses the platform through a web browser
- the browser sends requests to the Flask web application
- the Flask web application renders HTML templates and returns UI pages
- the Flask web application calls application services for authentication, listing management, request management, review management, favorite list management, and homepage recommendation
- the application services read from and write to the SQLite database
- the image utilities upload listing images to Amazon S3 and resolve public image URLs
- the AI one-click listing service sends image input to the Google Gemini API and receives draft listing output
- the Flask application runs inside a Docker container on AWS EC2

### Main Data Flow

1. The user opens the platform in a browser.
2. The browser sends a request to the Flask application.
3. The Flask application processes the request through the relevant service layer.
4. The service layer reads or updates data in SQLite when required.
5. If the action includes listing image handling, the application stores the image in Amazon S3 and keeps the object key in the database.
6. If the action uses AI one-click listing, the application sends the image to the Google Gemini API and receives a draft result.
7. The Flask application returns the final page or result to the browser.

### Deployment Scope

- one containerized Flask application running on AWS EC2
- one SQLite database file persisted on the EC2 host through a bind-mounted volume
- one Amazon S3 bucket for listing image storage
- Docker for containerization and deployment

## Supporting Design Artefacts

The supporting design artefacts for this project are maintained in the `diagram/` folder.
They help explain the system from different perspectives and are based on the design
decisions recorded in this document.

### ER Diagram Basis

The ER diagram should show the six main entities:

- `users`
- `categories`
- `listings`
- `requests`
- `reviews`
- `favorite_list`

The ER diagram should emphasise:

- primary keys and foreign keys
- seller, buyer, and reviewer relationships
- status fields for listings and requests
- the fact that `requests` stores both request flow and completed transaction state

### Use Case Diagram Basis

The use case diagram should use three actors:

- Visitor
- User
- Administrator

The use case diagram should highlight:

- guest browsing and public profile access
- user actions such as listing creation, request submission, favorites, reviews, and account management
- administrator monitoring and control actions without participation in buyer-seller transaction decisions

### Activity Diagram Basis

The activity diagram should centre on the core trading flow:

1. browse or search listings
2. view a listing and seller details
3. optionally save the listing
4. submit a purchase request
5. seller accepts or rejects
6. accepted listing moves to `pending`
7. buyer completes the transaction
8. request becomes `completed`
9. listing becomes `sold`
10. both sides may leave reviews

It can also show supporting flows such as AI-assisted listing creation and administrator review locking.

### Class Diagram Basis

The class diagram should reflect the main domain concepts:

- `User`
- `Administrator`
- `Listing`
- `Category`
- `Request`
- `Review`
- `FavoriteList`

The class diagram should make clear that:

- `Administrator` is a privileged role of `User`
- `User` can act as buyer or seller depending on the workflow
- `Request` links buyer, seller, and listing
- `Review` is created only after a completed request
- `FavoriteList` stores saved listing relationships per user

### System Architecture Diagram Basis

The system architecture diagram should show:

- browser access to the Flask application
- Flask routes, templates, and service-layer separation
- SQLite persistence for prototype data
- Amazon S3 for listing image storage
- Google Gemini as the external AI draft service
- Docker container runtime on AWS EC2
- session-based personalization for homepage recommendations

- `ER_diagram.drawio` shows the database entities and their relationships.
- `use_case_diagram.drawio` shows the main visitor, user, and administrator interactions.
- `activity_diagram.drawio` shows the core request and transaction workflow.
- `class_diagram_second_hand_platform_clean_fixed.drawio` shows the main domain classes.
- `system_architecture.drawio` shows the implemented runtime architecture on Flask, Docker, EC2, SQLite, S3, and Gemini.

Wireframes were not maintained as a separate design artefact in the current repository.
The implemented page structure was refined directly through template development and browser-based UI review.

## Scope Boundary

This document defines the technical system boundary so the diagrams and implementation stay aligned with the approved project scope. The first version excludes:

- shopping cart and multi-item checkout
- online payment integration
- multiple listing images or gallery management
- shipping, delivery tracking, or receiving workflow
- automatic completion after a timeout
- automatic default ratings or reviews
- live chat
- dispute handling
- transaction readiness indicator as a separate feature
- external market price integration
- advanced recommendation models
- vector database or heavy semantic search
- complex machine learning pipeline
