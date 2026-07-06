# System Design

### Second-Hand Trading Platform

*With AI One-Click Listing and Interest-Based Homepage Recommendation*

## System Scope

This system includes:

- guest browsing of listings and item details
- user registration and login
- user and administrator roles
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
- `image_url` - single listing image path or URL in the first version
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

## Table Relationships

- one `user` creates many `listings`
- one `category` contains many `listings`
- one `listing` receives many `requests`
- one `user` creates many `requests`
- one `user` receives many `requests` on owned listings
- one completed `request` can produce reviews
- one `user` writes many `reviews`
- one `user` receives many `reviews`
- one `user` saves many listings in `favorite_list`

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
- administrators can view accounts, view listings, delete inappropriate listings, lock user accounts, and lock request records, but they do not decide transaction outcomes for buyers and sellers
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
3. The AI service returns a draft title, draft category, and draft description.
4. The platform compares the result with similar listings already stored in the database.
5. The platform returns a rough price reference based on similar listings.
6. The seller reviews and edits the draft before publishing.

### Output

- draft title
- draft category
- draft description
- rough price reference based on similar platform listings

### Storage Rule

- `price_reference` is shown to the user during listing creation and is not stored as a standalone database field in the first version

### Boundaries

- the assistant generates a draft, not a final published listing
- the seller must review and confirm the result
- the price is a rough reference, not an exact valuation
- the first version uses one image only
- the first version does not use external market price data

## Homepage Recommendation Support

### Signals

- recent search keywords
- recent browsing behaviour
- recent favorite list behaviour
- mapped interest category from those interactions

### Recommendation Rule

- the homepage prioritises listings from the user's recent interest category

### Boundaries

- the first version uses lightweight rule-based logic
- the first version does not use a heavy recommendation engine, vector database, or complex machine learning pipeline

## ER Diagram Design

### Main Entities

- `users`
- `categories`
- `listings`
- `requests`
- `reviews`
- `favorite_list`

### Main Relationships

- one user creates many listings
- one category contains many listings
- one listing receives many requests
- one user creates many requests
- one user receives many requests on owned listings
- one completed request can have reviews
- one user writes many reviews
- one user receives many reviews

### Key Attributes

- primary keys
- foreign keys
- listing status
- request status
- preferred contact method
- review score

## Use Case Diagram Design

### Main Actors

- Visitor
- User
- Administrator

### Visitor Use Cases

- browse listings
- search listings
- filter listings
- view item details
- view public user profiles

### User Use Cases

- register account
- log in and log out
- edit profile
- browse listings
- search listings
- filter listings
- view item details
- view other user profiles
- create listing
- edit listing
- delete listing
- submit purchase request
- view request and transaction history
- save a listing to the favorite list
- remove a listing from the favorite list
- view the favorite list page
- confirm completed transaction
- receive homepage recommendations
- use AI one-click listing support when creating a listing
- leave a review after a completed transaction

### User Role Note

- the same account can act as both buyer and seller in different transactions

### Administrator Use Cases

- log in
- view user accounts
- view listings
- delete inappropriate listings
- lock user accounts
- lock request records
- view request records
- view completed request records

## Activity Diagram Design

### Main Activity Flow

1. A user logs in and browses or searches listings.
2. The user applies filters and views item details.
3. The user checks the seller profile and trust indicators.
4. The user can save the listing to the favorite list.
5. The user submits a purchase request.
6. The system stores the request with `pending` status.
7. The seller views incoming requests.
8. The seller accepts or rejects a request.
9. If accepted, the listing status becomes `pending`.
10. The buyer confirms transaction completion.
11. The request status becomes `completed`.
12. The listing status becomes `sold`.
13. Both users can leave reviews.
14. Trust indicators are updated.

### Additional Activity Flows

- AI one-click listing creation flow
- profile editing flow
- administrator control flow

## Class Diagram Design

### Main Classes

- `User`
- `Administrator`
- `FavoriteList`
- `Listing`
- `Category`
- `Request`
- `Review`

### Relationships

- `Administrator` is a privileged role of `User`
- `User` creates `Listing`
- `Listing` belongs to `Category`
- `User` submits `Request`
- `User` manages incoming requests on owned listings
- `Request` can result in `Review` after completion
- `User` saves `Listing` items into `FavoriteList`
- `User` holds profile information and trust indicators
- `Administrator` views users, listings, request records, and completed request records and applies control actions

### Core Attributes

- `User`: id, display_name, email, phone_number, preferred_contact_method, role, is_locked
- `Listing`: id, title, description, condition, price, status
- `Request`: id, status, is_locked, message, created_at
- `Review`: id, score, comment
- `FavoriteList`: id, user_id, listing_id
- `Category`: id, name

### Core Methods

- `User.editProfile()`
- `User.createListing()`
- `User.acceptRequest()`
- `User.rejectRequest()`
- `User.confirmCompletedTransaction()`
- `User.submitRequest()`
- `User.viewHomepageRecommendations()`
- `User.saveFavorite()`
- `User.removeFavorite()`
- `Administrator.viewUsers()`
- `Administrator.viewListings()`
- `Administrator.deleteInappropriateListing()`
- `Administrator.lockUserAccount()`
- `Administrator.lockRequestRecord()`

## System Architecture Diagram Design

### Main Components

- User Browser
- Flask Web Application
- HTML Templates and Bootstrap UI
- Application Services
- SQLite Database
- OpenAI API
- Docker Container
- Kubernetes Deployment

### Main Connections

- the user accesses the platform through a web browser
- the browser sends requests to the Flask web application
- the Flask web application renders HTML templates and returns UI pages
- the Flask web application calls application services for authentication, listing management, request management, review management, favorite list management, and homepage recommendation
- the application services read from and write to the SQLite database
- the AI one-click listing service sends image input to the OpenAI API and receives draft listing output
- the Flask application runs inside a Docker container
- Kubernetes deploys and manages the containerized application

### Main Data Flow

1. The user opens the platform in a browser.
2. The browser sends a request to the Flask application.
3. The Flask application processes the request through the relevant service layer.
4. The service layer reads or updates data in SQLite when required.
5. If the action uses AI one-click listing, the application sends the image to the OpenAI API and receives a draft result.
6. The Flask application returns the final page or result to the browser.

### Deployment Scope

- one containerized Flask application
- one SQLite database file used by the application
- Docker for containerization
- Kubernetes for deployment and management

## Wireframes Design

### Required Screens

- homepage
- login page
- register page
- listing browse page
- listing detail page
- create listing page
- AI one-click listing page
- favorite list page
- request history page
- public profile page
- administrator management page

### Wireframe Focus

- page layout
- navigation structure
- main form fields
- main buttons and actions
- search and filter placement
- homepage recommendation section placement
- AI one-click listing input and output area

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

## Additional Diagrams

- System Architecture Diagram
- Wireframes

## Diagram Priority

1. ER Diagram
2. Use Case Diagram
3. Activity Diagram
4. Class Diagram
5. System Architecture Diagram
6. Wireframes
