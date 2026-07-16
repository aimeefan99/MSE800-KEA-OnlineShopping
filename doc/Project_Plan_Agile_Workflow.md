# Agile Workflow

## Project Overview

### Second-Hand Trading Platform - Kea Marketplace

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

The implementation approach follows object-oriented programming and selected design patterns where appropriate.

## Agile Approach

This project follows a lightweight six-week Agile workflow suitable for a two-member team.

The team will work in short sprints, review progress regularly, and adjust tasks based on implementation progress. The workflow focuses on:

- delivering a working MVP early
- improving the system by sprint iteration
- keeping the scope realistic
- coordinating work clearly across the team
- testing and refining the system continuously

Each sprint is expected to deliver a testable and reviewable increment so the system can improve through continuous sprint iteration.

## Team Collaboration

This project uses a shared collaboration model across a two-member team.

Both team members will contribute across implementation and review activities, including:

- frontend development
- backend development
- database design and integration
- feature implementation
- testing and debugging
- documentation
- sprint review and retrospective
- deployment implementation and verification

Work will be coordinated by sprint tasks, feature groupings, and shared project standards rather than by a strict frontend-versus-backend split.

High-level responsibility areas are summarized below:

| Area | Main Responsibility |
|---|---|
| Project Management, Sprint Management, High Level Project Documents and Shared Technical Standards | Fan Fan |
| System Design, Flask Mapping and ALL Diagrams: System Architecture Diagram, Use Case Diagram, Activity Diagram, Class Diagram, ER Diagram | Mahima Hoque Mim |
| Core features: AI listing draft(Gemini), Account management, Listing Creation, Listing Browsing, Item Details, Favorites List, and Administrator Management  | Fan Fan |
| Core features: Smart Homepage, Search and Filter, Request and Transaction, Trust and Review, Administrator Request-Management, and UI Refinement | Mahima Hoque Mim |
| Deployment and AWS Cloud Setup: Docker, GitHub Actions, EC2 Hosting, S3 Image Storage, Environment Configuration, and Deployment Validation | Fan Fan |

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
- the related code review has been completed before merge to `main`
- the work has been committed and pushed to GitHub

## Scope Control

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

## Cost Management

The project was designed to keep operating costs low during development and demonstration:

- the AI listing feature uses the Gemini API free tier for low-volume prototype usage
- AWS deployment was kept within the AWS new-account credit model used by the project account
- Docker, EC2, and S3 were kept to a simple single-instance deployment design to avoid unnecessary infrastructure cost
- public cloud usage was limited to the services directly needed for hosting, image storage, and demonstration

Cost usage was monitored during implementation because some AWS resources, including Elastic IP usage, can still consume credit balance.

## MVP and Innovation Scope

### Core Features

The MVP scope covers the main second-hand marketplace workflow:

- visitors can browse, search, filter, and view listings without registering
- users can register, log in, edit profiles, and manage their own listings
- users can save favorites and submit purchase requests
- sellers can manage incoming requests and complete the basic transaction flow
- administrators can monitor users and listings and remove inappropriate content

### Innovation Features

The main innovation scope is limited to two features:

- AI-assisted listing draft generation from a single uploaded product image
- homepage recommendations based on recent user interest signals

## Product Backlog Priority

The detailed backlog was maintained in Jira. This document records backlog priority only at a summary level:

- `Must Have`: features required for the marketplace MVP and the two main differentiation features
- `Should Have`: important trust, usability, and refinement features
- `Could Have`: lower-priority enhancements that can be postponed without affecting the core demonstration

The Jira priority labels were aligned as follows:

- `Highest` or `High` -> `Must Have`
- `Medium` -> `Should Have`
- `Low` -> `Could Have`

## Sprint Management and Tracking

Detailed story status, sprint progress, and acceptance criteria were managed in Jira:

- https://aimeefan99.atlassian.net/jira/software/projects/MSE800/summary

## Sprint Structure

The sprint plan is intentionally kept at a summary level here. Detailed task tracking, assignees, and acceptance criteria were managed in Jira during implementation.

## Sprint 1: Project Setup and Requirements

Duration: `Week 1`

Sprint Goal:

- confirm project scope and prepare the shared technical foundation

Key Focus:

- define the product vision, scope, and differentiation points
- create and prioritise the backlog
- define functional requirements, shared routes, and development guidelines
- prepare system design, data model, and initial diagrams
- set up the repository, workflow, and initial Flask project structure

Key Stories:

- `MSE800-50` project vision, scope, and differentiation
- `MSE800-51` core requirements documentation
- `MSE800-52` backlog creation and prioritisation
- `MSE800-53` system architecture and module responsibilities
- `MSE800-54` data model and business rules
- `MSE800-55` shared routes, fields, and response rules
- `MSE800-56` development guidelines
- `MSE800-59` Flask usage documentation
- `MSE800-60` feasibility study

Expected Output:

- agreed scope and feature priorities
- shared project structure and working conventions
- initial technical documentation and diagrams
- development-ready backlog for implementation

## Sprint 2: Account and Listing Increment

Duration: `Week 2`

Sprint Goal:

- build the core account, listing, and browsing foundation

Key Focus:

- registration, login, logout, and profile editing
- listing creation, editing, deletion, and status handling
- browse listings, item details, keyword search, and filters
- establish the first working database-backed marketplace flow

Key Stories:

- `MSE800-1` register account
- `MSE800-2` log in and log out
- `MSE800-3` edit profile details
- `MSE800-4` create listing
- `MSE800-5` edit or delete listing
- `MSE800-12` browse listings
- `MSE800-13` search listings by keyword
- `MSE800-14` listing filters
- `MSE800-15` item details
- `MSE800-27` listing status display

Expected Output:

- working authentication flow
- working listing create, edit, delete, and browse flow
- searchable and filterable marketplace pages
- stable database foundation for later transaction features

## Sprint 3: Marketplace MVP Increment

Duration: `Week 3`

Sprint Goal:

- complete the first end-to-end marketplace transaction workflow

Key Focus:

- public profile viewing
- favorite list add and view flow
- purchase request submission and incoming request handling
- buyer-side completion flow
- initial administrator user and listing management

Key Stories:

- `MSE800-8` view incoming purchase requests
- `MSE800-9` accept or reject incoming purchase requests
- `MSE800-10` confirm completed transaction
- `MSE800-11` view another user's profile
- `MSE800-16` save items to favorites
- `MSE800-17` view favorite list
- `MSE800-18` submit a purchase request
- `MSE800-19` administrator views user accounts
- `MSE800-20` administrator views listings
- `MSE800-21` administrator deletes inappropriate listings

Expected Output:

- users can save listings and submit purchase requests
- listing owners can manage incoming requests
- administrators can monitor users and listings
- the core marketplace trading loop is functional

## Sprint 4: Core Differentiation Features

Duration: `Week 4`

Sprint Goal:

- implement the main differentiation features of the platform

Key Focus:

- AI-assisted listing draft generation from product images
- homepage recommendations based on recent interest signals
- ratings, reviews, and public trust indicators
- stronger public profile contact and credibility information

Key Stories:

- `MSE800-28` AI listing draft generation
- `MSE800-30` homepage recent-interest recommendations
- `MSE800-31` rating and review after completed transaction
- `MSE800-32` profile trust indicators
- `MSE800-33` public profile trust and contact information
- `MSE800-36` recommendation improvement after testing

Expected Output:

- AI listing assistant visible in the user flow
- recent-interest recommendations visible on the homepage
- trust-building features connected to completed transactions and profiles
- the platform's distinctive value clearly demonstrated

## Sprint 5: System Refinement Increment

Duration: `Week 5`

Sprint Goal:

- stabilize the system and prepare it for demonstration and deployment

Key Focus:

- request history and administrator request-record controls
- account and listing management refinements
- bilingual labels, UI polish, branding, and category improvements
- testing evidence, documentation, Docker, AWS deployment, S3 image storage, and secrets management

Key Stories:

- `MSE800-22` administrator request-record views
- `MSE800-23` administrator user lock
- `MSE800-24` administrator request-record lock
- `MSE800-25` request and transaction history
- `MSE800-57` testing strategy
- `MSE800-58` verification and validation evidence
- `MSE800-61` bilingual interface labels
- `MSE800-62` Māori principles and data sovereignty documentation
- `MSE800-63` Docker containerisation
- `MSE800-64` AWS deployment
- `MSE800-65` S3 image storage
- `MSE800-66` deployment configuration and secrets management
- `MSE800-69` category coverage improvement
- `MSE800-70` header logo
- `MSE800-72` UI polish and consistency
- `MSE800-73` account page and my listings management

Expected Output:

- refined administrator and account-management workflows
- improved usability and presentation quality
- completed testing and evidence documentation
- working Docker and AWS-based deployed environment with S3-backed listing images

## Sprint 6: Release Preparation Increment

Duration: `Week 6`

Sprint Goal:

- use the final week as a release buffer, final verification period, and submission preparation window

Key Focus:

- final README, diagrams, and report polishing
- final deployment verification and demo rehearsal
- defect fixes if required
- final presentation and submission preparation

Key Stories:

- no major new implementation stories were planned for this sprint

Expected Output:

- final report and presentation materials prepared
- live system verified for demonstration
- project ready for submission

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

## Out-of-Scope Features

To keep the project realistic for a two-person team, the following features are excluded from the main scope:

- shopping cart, multi-item checkout, and online payment
- live chat, shipping, delivery tracking, and dispute handling
- complex negotiation or automation features beyond the basic request flow
- multiple-image listing galleries and multi-image AI recognition
- external market price integration and advanced recommendation or search infrastructure

If time permits, the team may extend the project after the MVP and innovation features are complete.
