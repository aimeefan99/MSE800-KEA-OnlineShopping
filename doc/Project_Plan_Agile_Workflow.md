# Agile Workflow

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

## Team Collaboration

This project uses an equal-contribution collaboration model.

Both team members will participate in:

- frontend development
- backend development
- database design and integration
- feature implementation
- testing and debugging
- documentation
- sprint review and retrospective
- deployment implementation and verification

Work will be divided evenly by sprint tasks and project features rather than by fixed frontend or backend ownership.

## Technology Stack

- Backend: Python, Flask
- Frontend: HTML, CSS, Bootstrap
- Database: SQLite
- AI Integration: OpenAI API
- Containerization and Deployment: Docker, Kubernetes
- Version Control: GitHub
- Project Management: Trello or Jira
- Design Tool: draw.io

The implementation approach follows object-oriented programming and selected design patterns from the course where appropriate.

## Agile Ceremonies

### Sprint Planning

At the beginning of each sprint, the team will:

- confirm sprint goals
- select backlog items
- divide tasks equally
- estimate workload
- identify dependencies and risks

### Weekly Check-In

The team will hold short check-ins during the week to:

- report progress
- discuss blockers
- rebalance tasks if needed
- confirm integration progress

### Sprint Review

At the end of each sprint, the team will:

- demonstrate completed features
- verify whether sprint goals were achieved
- record unfinished items
- update the backlog

### Sprint Retrospective

After each sprint, the team will:

- identify what worked well
- identify what needs improvement
- improve task allocation and communication for the next sprint

## Definition of Done

A task will be considered complete when:

- the feature has been implemented
- it works in the local system
- related database changes are completed if required
- it is integrated into the main workflow
- basic testing has been completed
- the work has been committed and pushed to GitHub

## Delivery Boundary

The team will follow these priority boundaries during development:

- Must Have features must be completed before lower-priority features are expanded
- Should Have features will be developed after the MVP is stable
- Could Have features will only be included if time permits

If a core feature is incomplete, lower-priority enhancements will be delayed until the main system is working reliably.

To avoid unnecessary workload and scope creep, any newly suggested feature must be checked against the core marketplace workflow before being added to the main scope. Features that do not directly support user-to-user trading, the required innovation features, or the final assessment deliverables will be deferred as future extensions rather than added during the six-week implementation period.

## Risk Control

To keep the project realistic and manageable, the team will monitor a small number of key risks:

- AI integration risk: keep AI features lightweight and prepare a simple fallback if needed
- scope risk: prioritize MVP features before advanced enhancements
- integration risk: test feature integration at the end of each sprint
- deployment risk: prepare deployment early and keep the deployment environment aligned with the core system

## Product Backlog Priority

### Must Have

- guest browsing of listings and item details
- user registration
- user login and logout
- user and administrator roles
- profile editing with contact preference
- age verification during registration using date of birth
- create listing
- edit listing
- delete listing
- listing image upload
- browse listings
- search listings by keyword
- filter by category
- filter by condition
- filter by price range
- item detail page
- public user profile viewing
- favorite list support
- purchase request submission
- request management for listing owners
- sold status update after transaction completion
- administrator viewing of user accounts and listings
- administrator deletion of inappropriate listings
- AI one-click listing assistant
- interest-based homepage recommendation
- ratings and reviews for completed transactions
- profile trust indicators such as transaction count and rating summary

### Should Have

- better UI usability improvements

### Could Have

- request or transaction history view
- administrator viewing of request records and completed request records
- administrator locking of request records
- semantic-style search improvement only if time permits
- analytics dashboard
- flagged listing workflow
- recently viewed items support

## MVP and Innovation Scope

### Core Features

The core feature scope will be considered complete when the following platform capabilities are working:

1. Visitors can browse listings, search by keyword, apply filters, and view item details without registering.
2. Users can register, log in, and access the platform according to their role.
3. User registration includes age verification based on date of birth.
4. Users can edit core profile details, including phone number and preferred contact method.
5. Users can create, edit, and delete their own listings with clear listing status support.
6. Registered users can save interesting listings to a favorite list page.
7. Registered users can submit purchase requests through the platform.
8. Listing owners can view purchase requests and accept or reject them.
9. Buyers can confirm when a transaction is completed, and the related listing is then marked as sold.
10. Listings marked as `sold` no longer appear in normal browse and search results for available items.
11. Users can view basic request or transaction history.
12. Administrators can view user accounts, view listings, delete inappropriate listings, view request records and completed request records, and lock users or lock request records when needed without changing the transaction outcome directly.

Project completion also requires the innovation features defined below.

### Innovation Features

The innovation feature scope will be considered complete when the following features are working:

1. Sellers can upload one product image and receive a draft listing with a suggested item name, suggested category, short description draft, and a rough platform-based price reference.
2. The homepage can identify a user's recent interest category from search, browsing, and favorite list behaviour, then prioritise relevant listings for that user.

## Core User Stories

The product backlog is prioritised using three levels:

- `Must Have`: required for the MVP, the core trading workflow, or the two highlighted features.
- `Should Have`: important for usability and trust, but the platform can still run without them if time becomes tight.
- `Could Have`: useful improvements that can be postponed without breaking the main workflow or the feature demo.

The backlog also aligns to Jira priority labels as follows:

- `Highest` or `High`: Must Have
- `Medium`: Should Have
- `Low`: Could Have
- `Lowest`: reserved for ideas that are explicitly parked outside the current delivery plan

### Must Have

#### Access and Core Platform Entry

- As a visitor, I want to browse listings without registering so that I can explore the platform before creating an account.
- As a visitor, I want to search listings and view item details without logging in so that I can decide whether the platform has items I am interested in.
- As a user, I want to register an account so that I can use the platform.
- As a user, I want to log in and log out securely so that I can access my personal features safely.

#### Listing and Selling Workflow

- As a user, I want to create a listing so that I can offer an item for sale on the platform.
- As a user, I want to edit or delete my listing so that I can keep item information accurate.
- As a user, I want to upload one product image and receive a draft listing so that I can publish items much faster than filling every field manually.
- As a user, I want to view incoming purchase requests on my listings so that I can manage interested buyers.
- As a user, I want to accept or reject incoming purchase requests on my listings so that the transaction process is clear.
- As a user, I want to confirm a completed transaction so that the related listing is updated to sold correctly.

#### Buying and Discovery Workflow

- As a user, I want to browse listings so that I can discover available items on the platform.
- As a user, I want to search listings by keyword so that I can quickly find relevant products.
- As a user, I want to use filters such as category, condition, and price range so that I can narrow search results efficiently.
- As a user, I want to view item details so that I can decide whether I am interested in a product.
- As a user, I want to save interesting items to a favorite list so that I can revisit them later.
- As a user, I want to view my favorite list page so that I can manage saved items.
- As a user, I want to submit a purchase request so that I can express interest in buying an item.
- As a user, I want the homepage to recommend listings from categories I recently searched, browsed, or saved so that discovery feels more relevant to my current interest.

#### Administrator Control

- As an administrator, I want to view user accounts so that I can monitor platform safety.
- As an administrator, I want to view listings so that I can inspect platform content when needed.
- As an administrator, I want to delete inappropriate listings so that clearly unsuitable content can be removed from the platform.

### Should Have

#### Profile, Trust, and Communication

- As a user, I want to edit my profile details so that my account information and contact preference stay up to date.
- As a user, I want to set my preferred contact method to email or phone so that other users know the best way to contact me.
- As a user, I want to view another user's profile so that I can understand credibility before responding to a request.
- As a user, I want to leave a rating or review after a completed transaction so that trust can be built between users.
- As a user, I want to view profile trust indicators such as completed transactions and positive feedback so that I can judge reliability more easily.
- As a user, I want my public profile to show key trust and contact information so that marketplace communication is more practical and transparent.

#### Administration and Record Tracking

- As an administrator, I want to lock a user account when necessary so that unsafe or inappropriate activity can be controlled.
- As an administrator, I want to view request records and completed request records so that I can monitor platform activity responsibly.
- As a user, I want to view my request or transaction history so that I can track my activity on the platform.

### Could Have

#### Secondary Administrative and Usability Enhancements

- As an administrator, I want to lock a request record when necessary so that a problematic case can be frozen for review without manually changing its result.
- As an administrator, I want to view request records and completed request records so that I can monitor platform activity responsibly.
- As a user, I want to view my request or transaction history so that I can track my activity on the platform.
- As a user, I want to view another user's profile so that I can understand credibility before responding to a request.
- As a user, I want to set my preferred contact method to email or phone so that other users know the best way to contact me.

## Sprint Structure

## Sprint 1: Project Setup and Requirements

Duration:

- Week 1

Sprint Goal:

- confirm requirements and establish the technical foundation

Highlight Tasks:

- finalize project scope
- confirm the user and administrator role model
- define MVP features
- define out-of-scope features
- confirm core user stories
- review reference platforms such as Trade Me
- identify the project point of difference
- confirm the AI one-click listing concept
- confirm the homepage recommendation logic
- create use case diagram
- create ER diagram
- create activity diagram
- sketch main page structure
- set up GitHub repository
- set up Trello or Jira board
- initialize Flask project structure
- prepare database schema draft

Frontend / UI Tasks:

- sketch wireframes for the main pages
- define page structure and navigation flow
- confirm the main user journey for user and administrator interfaces

Backend / System Tasks:

- initialize Flask project structure
- prepare the initial database schema draft
- confirm the main entities and workflow relationships

Deployment / DevOps Tasks:

- set up GitHub repository and branch workflow
- set up Trello or Jira board
- confirm Docker and Kubernetes deployment direction

Detailed User Stories:

- `Priority: Medium | Should Have` As a project team, we want to document how Māori principles and Māori Data Sovereignty are considered in our project so that our cultural, ethical, and data-handling decisions are clearly explained.

- Core user stories are reviewed, prioritised, and translated into backlog items for implementation.
- This sprint makes sure the following development work is based on clear user needs, agreed scope boundaries, and a shared system structure.

Expected Output:

- confirmed project scope
- prioritized user stories completed
- key diagrams completed
- project structure set up
- initial backlog created

## Sprint 2: Account and Listing Increment

Duration:

- Week 2

Sprint Goal:

- build the core account and listing management system

Highlight Tasks:

- implement user registration
- implement age verification during registration using date of birth
- implement login and logout
- implement user and administrator role handling
- implement basic administrator access control foundation
- create database tables for users, listings, categories, and requests
- create database support for favorite list
- create database support for listing status foundation
- implement create listing
- implement listing image support
- implement edit listing
- implement delete listing
- implement browse listings page
- implement item detail page
- implement search by keyword
- implement practical filters such as category, condition, and price range
- implement basic page templates and forms
- test authentication workflow
- test listing creation and browsing workflow

Frontend / UI Tasks:

- build register and login pages
- build profile edit page
- build listing form and listing management page
- include listing image input in listing forms
- build browse listings page and item detail page
- build search and filter interface
- build favorite list page structure
- connect the first account and listing pages to the backend

Backend / System Tasks:

- implement registration, login, and logout logic
- implement age verification logic during registration
- implement user and administrator role handling
- implement basic administrator access control foundation
- create users, listings, categories, and requests tables
- create favorite list table
- add editable profile fields such as phone number and preferred contact method
- add support for listing status foundation
- add listing image field support for listings
- implement listing create, edit, and delete logic
- implement listing browse, item detail, keyword search, and filter logic

Deployment / DevOps Tasks:

- prepare Docker-related project structure
- confirm the application can run consistently in the local development environment

Detailed User Stories:

- `Priority: Highest | Must Have` As a user, I want to register an account so that I can use the platform.
- `Priority: Highest | Must Have` As a user, I want to log in and log out securely so that I can access my personal features safely.
- `Priority: Highest | Must Have` As a user, I want to browse listings so that I can discover available items on the platform.
- `Priority: Highest | Must Have` As a user, I want to search listings by keyword so that I can quickly find relevant products.
- `Priority: High | Must Have` As a user, I want to use filters such as category, condition, and price range so that I can narrow search results efficiently.
- `Priority: High | Must Have` As a user, I want to view item details so that I can decide whether I am interested in a product.
- `Priority: Highest | Must Have` As a user, I want to create a listing so that I can sell an item.
- `Priority: High | Must Have` As a user, I want to edit or delete my listing so that I can keep item information accurate.
- `Priority: High | Must Have` As a user, I want to see listing status such as available, pending, or sold so that I understand the current trading state of an item.
- `Priority: Medium | Should Have` As a user, I want to edit my profile details, including preferred contact method and related contact details, so that my account information stays up to date.
- `Priority: Low | Could Have` As a user, I want to set my preferred contact method to email or phone so that other users know the best way to contact me.

Expected Output:

- authentication working
- users can manage their own listings
- users can browse and search listings
- database schema implemented
- basic UI pages connected to backend

## Sprint 3: Marketplace MVP Increment

Duration:

- Week 3

Sprint Goal:

- complete the main user-to-user transaction flow

Highlight Tasks:

- implement public user profile view pages
- implement favorite list add and view flow
- implement purchase request submission
- implement incoming request view for listing owners
- implement request actions such as accept, reject, and complete
- implement buyer confirmation of completed transaction
- update sold status after completion confirmation
- implement basic administrator pages for viewing users and listings
- implement administrator deletion of inappropriate listings
- test end-to-end marketplace workflow
- fix integration issues

Frontend / UI Tasks:

- build public user profile view pages
- build favorite list page
- build purchase request form or action flow
- build listing owner request management page
- build basic administrator management pages

Backend / System Tasks:

- implement public user profile data support
- implement favorite list add and retrieval logic
- implement purchase request submission
- implement request handling actions such as accept, reject, and complete
- implement buyer confirmation of completed transaction
- update sold status after completion confirmation
- implement administrator listing deletion support
- implement basic administrator user and listing views
- prepare lightweight recommendation data foundations

Deployment / DevOps Tasks:

- prepare containerized MVP build
- verify the marketplace MVP can run in the intended deployment setup

Detailed User Stories:

- `Priority: Low | Could Have` As a user, I want to view another user's profile so that I can understand credibility before making or accepting a request.
- `Priority: High | Must Have` As a user, I want to save interesting items to a favorite list so that I can revisit them later.
- `Priority: High | Must Have` As a user, I want to view my favorite list page so that I can manage saved items.
- `Priority: Highest | Must Have` As a user, I want to submit a purchase request so that I can express interest in buying an item.
- `Priority: Highest | Must Have` As a user, I want to view incoming purchase requests on my listings so that I can manage interested buyers.
- `Priority: Highest | Must Have` As a user, I want to accept or reject incoming purchase requests on my listings so that the transaction process is clear.
- `Priority: Highest | Must Have` As a user, I want to confirm when a transaction is completed so that the platform can close the trading process correctly.
- `Priority: High | Must Have` As an administrator, I want to view user accounts so that I can monitor platform safety.
- `Priority: High | Must Have` As an administrator, I want to view listings so that I can inspect platform content when needed.
- `Priority: High | Must Have` As an administrator, I want to delete inappropriate listings so that unsuitable content can be removed from the platform.

Expected Output:

- users can submit purchase requests
- listing owners can manage requests
- administrators can view users and listings and delete inappropriate listings
- public profile viewing is available
- favorite list support is available
- core marketplace workflow completed

## Sprint 4: Core Differentiation Features

Duration:

- Week 4

Sprint Goal:

- complete the two signature features that distinguish the platform from a standard marketplace flow

Highlight Tasks:

- implement AI image upload flow for one-click listing draft generation
- connect uploaded listing images to the AI service
- generate suggested item name, category, and description draft from the uploaded image
- generate a rough platform-based price reference using similar listings in the database
- build homepage recommendation logic based on recent search, browsing, and favorite list behaviour
- connect homepage recommendation results to the main user landing page
- implement a simple rating and review feature for completed transactions
- implement profile trust indicators such as completed transactions and positive feedback
- connect trust information to public profile and transaction pages
- test whether AI listing draft output is useful and relevant
- test whether homepage recommendations are noticeably more relevant than fixed generic content

Frontend / UI Tasks:

- build AI one-click listing assistant interface
- build image upload and draft preview flow
- display homepage recommendation sections based on detected interest category
- build rating and review form
- display profile trust indicators
- display preferred contact method and selected contact details on public profiles

Backend / System Tasks:

- implement image upload handling for AI listing draft generation
- call the AI service for item recognition and listing draft generation
- implement platform-database-based rough price estimation using similar listings
- implement homepage recommendation logic based on interest category signals
- implement rating and review logic for completed transactions
- calculate profile trust indicators such as completed transactions and positive feedback
- support public profile display for transaction count, rating summary, and preferred contact method

Deployment / DevOps Tasks:

- update the deployed application structure for AI and review-related features
- verify deployment compatibility after the new feature integration

Detailed User Stories:

- `Priority: Highest | Must Have` As a user, I want to upload one product image and receive a listing draft so that I can publish an item faster.
- `Priority: Highest | Must Have` As a user, I want the platform to suggest an item name, category, description, and rough price reference so that creating a listing feels easier and more informed.
- `Priority: Highest | Must Have` As a user, I want the homepage to surface listings related to my recent interest category so that item discovery feels more relevant than a fixed general marketplace homepage.
- `Priority: Medium | Should Have` As a user, I want to leave a rating or review after a completed transaction so that trust can be built between users.
- `Priority: Medium | Should Have` As a user, I want to view profile trust indicators such as completed transactions and positive feedback so that I can judge reliability more easily.
- `Priority: Medium | Should Have` As a user, I want my public profile to show key trust and contact information so that marketplace communication is more practical and transparent.

Expected Output:

- AI one-click listing assistant working
- interest-based homepage recommendation working
- ratings and reviews feature working for completed transactions
- public trust indicators visible in profiles
- the platform's unique value is clearly visible in the demo

## Sprint 5: System Refinement Increment

Duration:

- Week 5

Sprint Goal:

- stabilize the system and improve usability

Highlight Tasks:

- implement request or transaction history view
- implement administrator view of request records and completed request records
- implement administrator user and request record locking actions
- fix bugs
- improve UI and usability
- run user testing
- run integration testing
- refine homepage recommendation quality and AI listing draft usability based on testing feedback
- refine diagrams and documentation
- prepare screenshots and testing evidence
- review unresolved issues
- update final backlog status
- rehearse final presentation and demo

Frontend / UI Tasks:

- improve layout consistency and usability
- refine user flow based on testing feedback
- polish key pages for final demonstration

Backend / System Tasks:

- implement request or transaction history view
- implement administrator request record and completed request record support
- implement administrator user and request record locking support
- fix bugs in implemented features
- improve integration reliability across modules
- refine data handling and system stability
- tune homepage recommendation logic and AI listing draft behaviour where needed

Deployment / DevOps Tasks:

- test the integrated system in the deployment environment
- refine configuration issues before final release

Detailed User Stories:

- `Priority: Low | Could Have` As a user, I want to view my request or transaction history so that I can track my activity on the platform.
- `Priority: Low | Could Have` As an administrator, I want to view request records and completed request records so that I can monitor platform activity responsibly.
- `Priority: High | Must Have` As an administrator, I want to lock a user account when necessary so that unsafe or inappropriate activity can be controlled.
- `Priority: Low | Could Have` As an administrator, I want to lock a request record when necessary so that a problematic case can be frozen for review without manually changing its result.
- `Priority: Medium | Should Have` As a user, I want the main platform pages to be easier to use so that buying, selling, and browsing feel smoother.
- `Priority: Medium | Should Have` As a user, I want homepage recommendations to be improved after testing so that the feature quality feels more useful in practice.
- `Priority: Low | Could Have` As a visitor, I want to see bilingual interface labels so that the platform feels more inclusive and culturally aware.

Expected Output:

- request or transaction history available
- administrator request record and locking features available
- bugs reduced across core workflows
- usability improvements applied to key pages
- testing evidence prepared
- system more stable for final release

## Sprint 6: Release Preparation Increment

Duration:

- Week 6

Sprint Goal:

- finalize deliverables, deployment, and submission

Highlight Tasks:

- complete README and technical documentation
- deploy the application to a live platform
- complete final testing check
- finalize diagrams and evidence
- complete presentation and demo preparation
- conduct final submission review

Frontend / UI Tasks:

- complete final UI verification in the live environment
- prepare screenshots and demo-ready page flow

Backend / System Tasks:

- complete final technical verification of implemented features
- confirm the system is stable for demonstration and submission

Deployment / DevOps Tasks:

- deploy the application to a live Kubernetes-based environment
- verify the deployed version is accessible and functional
- complete final deployment check before submission

Detailed User Stories:

- As a user, I want the completed platform features to work in the deployed environment so that the final system can be demonstrated clearly.

Expected Output:

- final report materials prepared
- deployment completed
- project ready for final submission

## Deliverables by the End of the Project

- working web-based second-hand trading platform
- user and administrator workflows
- AI one-click listing assistant
- interest-based homepage recommendation
- GitHub repository
- diagrams
- testing evidence
- final documentation
- deployed live version

## Workflow Notes

To keep the project realistic for a two-person team, the following features are excluded from the main scope:

- shopping cart and multi-item checkout
- online payment
- live chat
- shipping, delivery tracking, and receiving workflow
- dispute handling
- complex negotiation workflow
- automatic timeout-based completion
- automatic default ratings or reviews
- multiple image gallery support for each listing
- multi-image AI recognition for listing generation
- transaction readiness indicator as a separate feature
- external market price integration
- advanced recommendation engine
- vector database or heavy semantic search infrastructure
- complex machine learning pipeline

If time permits, the team may extend the project after the MVP and innovation features are complete.
