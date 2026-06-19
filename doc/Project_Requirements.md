## Project Overview

### Second-Hand Trading Platform

*With AI One-Click Listing and Interest-Based Homepage Recommendation*

This project is a web-based second-hand trading platform that supports the main user and administrator workflows in a realistic marketplace setting. Visitors can browse listings, search products, apply filters, and view item details before signing in. Registered users can then create listings, save interesting items, submit purchase requests, track request history, complete transactions, and leave reviews. A standard user account can act as both buyer and seller through different actions in the system, while administrators manage platform operations.

The project also draws on a review of mainstream second-hand trading platforms in New Zealand, especially Trade Me. That review highlighted two practical gaps:
- Trade Me still uses a traditional multi-step listing flow in which users must manually fill in all fields before publishing an item. 
- Trade Me tends to show relatively fixed and general homepage content to different users

In response, our project focuses on two highlighted features that are practical and clearly differentiated from a standard marketplace flow:

- `AI One-Click Listing Assistant`
  - helps users generate a draft listing from a product photo instead of manually filling every field from scratch
- `Interest-Based Homepage Recommendation`
  - makes homepage discovery more relevant to a user's recent interest instead of showing similar fixed homepage content to different users

The project will also be deployed as a live containerised system and refined through user testing.

## Agile Approach

This project follows a lightweight six-week Agile workflow suitable for a two-member team.

The team will work in short sprints, review progress regularly, and adjust tasks based on implementation progress. The workflow focuses on:

- delivering a working MVP early
- improving the system by sprint iteration
- keeping the scope realistic
- sharing work equally across the team
- testing and refining the system continuously

Each sprint is expected to deliver a testable and reviewable increment so the system can improve through continuous sprint iteration.

# Project Requirements

## Functional Requirements

| ID | Priority | Category | Requirement |
|---|---|---|---|
| FR-1 | Must Have | Access and Core Platform Entry | As a visitor, I want to browse listings without registering so that I can explore the platform before creating an account. |
| FR-2 | Must Have | Access and Core Platform Entry | As a visitor, I want to search listings and view item details without logging in so that I can decide whether the platform has items I am interested in. |
| FR-3 | Must Have | Access and Core Platform Entry | As a user, I want to register an account so that I can use the platform. |
| FR-4 | Must Have | Access and Core Platform Entry | As a user, I want to log in and log out securely so that I can access my personal features safely. |
| FR-5 | Must Have | Listing and Selling Workflow | As a user, I want to create a listing so that I can offer an item for sale on the platform. |
| FR-6 | Must Have | Listing and Selling Workflow | As a user, I want to edit or delete my listing so that I can keep item information accurate. |
| FR-7 | Must Have | Listing and Selling Workflow | As a user, I want to upload one product image and receive a draft listing so that I can publish items much faster than filling every field manually. |
| FR-8 | Must Have | Listing and Selling Workflow | As a user, I want to view incoming purchase requests on my listings so that I can manage interested buyers. |
| FR-9 | Must Have | Listing and Selling Workflow | As a user, I want to accept or reject incoming purchase requests on my listings so that the transaction process is clear. |
| FR-10 | Must Have | Listing and Selling Workflow | As a user, I want to confirm a completed transaction so that the related listing is updated to sold correctly. |
| FR-11 | Must Have | Buying and Discovery Workflow | As a user, I want to browse listings so that I can discover available items on the platform. |
| FR-12 | Must Have | Buying and Discovery Workflow | As a user, I want to search listings by keyword so that I can quickly find relevant products. |
| FR-13 | Must Have | Buying and Discovery Workflow | As a user, I want to use filters such as category, condition, and price range so that I can narrow search results efficiently. |
| FR-14 | Must Have | Buying and Discovery Workflow | As a user, I want to view item details so that I can decide whether I am interested in a product. |
| FR-15 | Must Have | Buying and Discovery Workflow | As a user, I want to save interesting items to a favorite list so that I can revisit them later. |
| FR-16 | Must Have | Buying and Discovery Workflow | As a user, I want to view my favorite list page so that I can manage saved items. |
| FR-17 | Must Have | Buying and Discovery Workflow | As a user, I want to submit a purchase request so that I can express interest in buying an item. |
| FR-18 | Must Have | Buying and Discovery Workflow | As a user, I want the homepage to recommend listings from categories I recently searched, browsed, or saved so that discovery feels more relevant to my current interest. |
| FR-19 | Must Have | Administrator Control | As an administrator, I want to view user accounts so that I can monitor platform safety. |
| FR-20 | Must Have | Administrator Control | As an administrator, I want to view listings so that I can inspect platform content when needed. |
| FR-21 | Must Have | Administrator Control | As an administrator, I want to delete inappropriate listings so that clearly unsuitable content can be removed from the platform. |
| FR-22 | Should Have | Profile, Trust, and Communication | As a user, I want to edit my profile details so that my account information and contact preference stay up to date. |
| FR-23 | Should Have | Profile, Trust, and Communication | As a user, I want to set my preferred contact method to email or phone so that other users know the best way to contact me. |
| FR-24 | Should Have | Profile, Trust, and Communication | As a user, I want to view another user's profile so that I can understand credibility before responding to a request. |
| FR-25 | Should Have | Profile, Trust, and Communication | As a user, I want to leave a rating or review after a completed transaction so that trust can be built between users. |
| FR-26 | Should Have | Profile, Trust, and Communication | As a user, I want to view profile trust indicators such as completed transactions and positive feedback so that I can judge reliability more easily. |
| FR-27 | Should Have | Profile, Trust, and Communication | As a user, I want my public profile to show key trust and contact information so that marketplace communication is more practical and transparent. |
| FR-28 | Should Have | Administration and Record Tracking | As an administrator, I want to lock a user account when necessary so that unsafe or inappropriate activity can be controlled. |
| FR-29 | Should Have | Administration and Record Tracking | As an administrator, I want to view request records and completed request records so that I can monitor platform activity responsibly. |
| FR-30 | Should Have | Administration and Record Tracking | As a user, I want to view my request or transaction history so that I can track my activity on the platform. |
| FR-31 | Could Have | Secondary Administrative and Usability Enhancements | As an administrator, I want to lock a request record when necessary so that a problematic case can be frozen for review without manually changing its result. |
| FR-32 | Could Have | Secondary Administrative and Usability Enhancements | As an administrator, I want to view request records and completed request records so that I can monitor platform activity responsibly. |
| FR-33 | Could Have | Secondary Administrative and Usability Enhancements | As a user, I want to view my request or transaction history so that I can track my activity on the platform. |
| FR-34 | Could Have | Secondary Administrative and Usability Enhancements | As a user, I want to view another user's profile so that I can understand credibility before responding to a request. |
| FR-35 | Could Have | Secondary Administrative and Usability Enhancements | As a user, I want to set my preferred contact method to email or phone so that other users know the best way to contact me. |

## Non-Functional Requirements

| ID | Requirement | Implementation Approach | Verification Method |
|---|---|---|---|
| NFR-1 | The system shall load core pages within 3 seconds under normal local demo conditions. | Keep Flask routes lightweight, use efficient SQL queries, limit unnecessary data loading, and keep uploaded images reasonably sized. | Measure response times for `/login`, `/register`, `/listings`, and `/listings/<id>` using browser developer tools. |
| NFR-2 | The system shall store passwords only as hashed values and shall never store passwords in plain text. | Use password hashing during registration and hash verification during login. Store only `password_hash` in the database. | Inspect the authentication code and confirm the database stores hashed values instead of readable passwords. |
| NFR-3 | The system shall require authentication for protected actions and prevent unauthorized access to private operations. | Apply login protection to actions such as creating listings, saving favorites, editing profiles, and submitting requests. Check ownership before allowing listing edits or deletion. | Attempt protected actions while logged out and confirm redirection to the login page. Attempt editing another user's listing and confirm access is denied. |
| NFR-4 | The system shall handle invalid or incomplete input without crashing and shall return a clear error message to the user. | Perform server-side validation for registration, login, and listing forms. Re-render the page with validation feedback when submission fails. | Submit incomplete or invalid forms and confirm the system shows an error message instead of returning a server error. |
| NFR-5 | The database shall maintain referential integrity between users, listings, categories, requests, reviews, and favorites. | Define foreign key relationships in the schema and validate related records before saving business data. | Review the schema and confirm valid foreign key definitions. Test that invalid references are not accepted through normal workflows. |
| NFR-6 | Public pages such as listings and item detail pages shall remain accessible without login whenever the application server is running. | Keep public browse and detail routes outside authentication protection and ensure missing optional data is handled gracefully. | Access `/listings` and `/listings/<id>` while logged out and confirm both pages load successfully. |
| NFR-7 | The system shall function correctly in at least two modern desktop browsers used for project demonstration. | Use standard HTML, CSS, Bootstrap, and Flask templates without browser-specific dependencies. | Test key workflows in at least two browsers, such as Chrome and Edge, and confirm that navigation, forms, and page rendering work correctly. |
| NFR-8 | The codebase shall be organized into separate modules for routes, services, models, templates, and static assets to support team collaboration and maintenance. | Keep the current layered project structure and place business logic in the service layer instead of mixing it into templates or route handlers. | Review the project structure and confirm new features follow the same separation of concerns. |
| NFR-9 | The project shall provide a documented way to recreate the database schema and restore required demo data after local data loss. | Maintain an initialization script and a shared demo database or repeatable seed process. Document the recovery steps clearly. | Rebuild the schema from scratch and confirm that required demo users, listings, and related records can be restored successfully. |
