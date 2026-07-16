# Feasibility Study

## 1. Purpose

This document records the early feasibility study for the `Second-Hand Trading Platform - Kea Marketplace`
project. It explains why we chose this project, what scope decisions we made at the
beginning, and why the project was realistic for a two-person, six-week software
engineering project.

The study follows the main feasibility dimensions used in software feasibility analysis:

- technical feasibility
- operational feasibility
- market feasibility
- cost and schedule feasibility
- legal and regulatory feasibility

## 2. Project Idea and Why We Chose It

The project idea was to build a web-based second-hand trading platform that allows:

- visitors to browse listings without logging in
- registered users to create listings and upload one product image
- buyers to submit purchase requests
- sellers to accept, reject, and complete transactions
- administrators to monitor users and listings

We chose this project because second-hand trading is familiar, practical, and easy to
explain in a New Zealand context. It also gives us enough room to demonstrate important
software engineering work such as requirements analysis, role-based access control,
database design, testing, and deployment planning.

We also wanted the project to include two features that go beyond a basic marketplace:

- an AI-assisted listing draft flow
- interest-based homepage recommendation

These features made the project more meaningful than a simple CRUD listing system while
still being realistic for a prototype.

## 3. Project Scope Decisions

At the start of the project, we had to decide how much marketplace functionality was
realistic within the available time.

Several larger ideas were intentionally excluded from the first version:

- full shopping cart
- full order management system
- integrated online payment
- multi-image gallery per listing
- advanced multi-step moderation workflow

These features were too large for the available schedule and would have added a lot of
extra complexity to the database, workflow states, and testing.

This did not remove basic administrator moderation features already planned for the
project, such as viewing users, viewing listings, and deleting inappropriate listings.
It only meant that more complex moderation processes were kept out of the first version.

Instead, we chose a lighter marketplace workflow:

- buyer submits a purchase request
- seller accepts or rejects the request
- buyer confirms completion
- listing status is updated accordingly

This decision kept the trading flow realistic enough for the project while controlling
implementation risk. It also fits a second-hand marketplace model better than a full
shopping cart and checkout system.

## 4. Technical Feasibility

The project was technically feasible because the selected stack was suitable for a
prototype and also realistic for our learning level.

### 4.1 Backend

`Flask` was a feasible backend choice because it is lightweight, easy to organize with
blueprints, and suitable for an MVP-style web system. It also allowed the project to be
split into clear modules for:

- authentication
- listings
- transactions
- profiles
- administration
- AI and recommendation features

This made Flask a good fit for a two-developer project where both clarity and speed of
development mattered.

### 4.2 Frontend

`HTML`, `CSS`, and `Bootstrap` were feasible because they supported server-rendered pages
without needing a separate frontend framework. This kept the project simpler and let us
focus on the main platform workflows.

### 4.3 Database

`SQLite` was technically feasible for the project because:

- the application scope was moderate
- the expected demo workload was low
- it allowed fast local development
- it avoided the extra setup overhead of a larger database server

SQLite was suitable for our prototype, even though a real production marketplace would
usually use a stronger database platform.

### 4.4 AI Feature

Using the `Google Gemini API` for AI-assisted listing draft generation was feasible because we
only needed a simple assisted workflow. The AI output is treated as a draft suggestion,
not as final product data.

### 4.5 Deployment

Deployment using `Docker` and cloud hosting on `AWS` was technically feasible because
containerization is a practical way to package a Flask system for demonstration and final
presentation.

Containerized deployment was part of the intended direction, while more advanced cloud
automation was treated as later-stage work rather than a dependency for core feature
completion.

## 5. Operational Feasibility

The system was operationally feasible because its main user flows were simple and easy to
understand:

- visitors browse listings
- users register and log in
- sellers create listings
- buyers submit purchase requests
- sellers manage those requests
- completed items move to sold status

The platform also supports public seller information and preferred contact methods, which
are useful for marketplace communication.

From a user point of view, the workflow is practical because it reflects a lightweight
second-hand trading process rather than a complex retail checkout system.

From a team point of view, the project was also operationally feasible because the work
could be split by feature while still following shared route, template, and service
rules.

## 6. Market Feasibility

The project was market-feasible at concept level because second-hand trading platforms
are widely used and familiar to users. In the New Zealand context, platforms such as
`Trade Me` show that there is already strong demand for second-hand item discovery and
buyer-seller interaction.

The project was also supported by two practical ideas that helped differentiate it:

- reducing listing effort through AI-assisted draft generation
- improving homepage discovery through interest-based recommendation

These ideas respond to common marketplace pain points:

- manual listing creation takes time
- general browsing pages may not reflect user interest well

Based on that, we felt the project idea was not only technically possible but also worth
building as a marketplace prototype.

## 7. Cost and Schedule Feasibility

The project was feasible within the available academic constraints because the scope was
deliberately limited to a prototype-level implementation.

### 7.1 Cost Feasibility

From a budget perspective, the project was feasible because it could be developed mainly
with free or low-cost tools and services.

The project did not require major upfront funding for:

- software licenses
- specialist hardware
- paid database infrastructure
- real payment gateway integration

Most of the chosen technologies were free to use for development and academic work:

- Flask
- SQLite
- HTML, CSS, and Bootstrap
- GitHub
- draw.io

Potential cloud-related costs were also controllable because:

- deployment could remain optional until later project stages
- AWS usage could be limited to small-scale or free-tier experimentation
- Amazon S3 image storage would involve only a small amount of data for a prototype

The main cost risk came from external API usage, especially the AI-assisted listing
feature. That risk was still manageable because the project only required limited
prototype-level usage.

Overall, the project was financially feasible for a student team because the expected
costs were low and the scope avoided expensive integrations such as full online payment
processing.

### 7.2 Schedule Feasibility

The project was feasible for a two-person, six-week timeline because:

- Sprint 1 focused on planning and documentation
- implementation started from Sprint 2
- the core workflows were prioritized before optional trust and refinement features
- several advanced features were explicitly excluded from the MVP scope

Without this scope control, the project would not have been realistically deliverable in
the available time.

## 8. Legal and Regulatory Feasibility

The project was legally feasible as an academic prototype because it does not process real
financial transactions or operate as a real commercial platform.

Even so, several basic legal and ethical considerations were still relevant:

- user passwords must be stored as hashes rather than plain text
- user contact details should only be shown according to the designed public profile rules
- uploaded content should be manageable through administrator moderation
- the platform should avoid presenting AI-generated content as guaranteed factual output

Because the system does not include real payment handling, banking integration, or formal
consumer contract processing, it avoids many of the regulatory burdens that would apply
to a fully commercial online marketplace.

## 9. Conclusion

The project was feasible as a software engineering prototype.

It was technically achievable with the chosen stack, understandable for users, relevant
as a second-hand trading concept, and manageable within the cost and schedule limits of a
two-person academic project.

The main reason it stayed feasible was that we kept the scope under control. Instead of
turning it into a full e-commerce system with shopping cart, order management, and
payment, we kept the request-based marketplace flow and focused on building a realistic,
testable, and presentable solution.
