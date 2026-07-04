# Māori Principles and Data Sovereignty

## 1. Introduction

This project is a second-hand trading platform, so it stores user data such as account
details, contact information, listing images, and request records. Because of that, the
project is not only about building features. It also involves decisions about what data
is collected, who can see it, how long it is kept, and who is allowed to act on it.

The Māori principles introduced in class were useful because they pushed us to think
about data in a more responsible and people-centred way. In this project, we did not try
to add cultural content just for appearance. Instead, we used these principles to guide
practical decisions around privacy, user control, trust, and responsibility throughout
the development process.

## 2. How These Principles Apply to This Project

For our project, the strongest connection to these principles is in how we handle user
data, access control, and responsibility for platform actions.

### 2.1 Pūkenga and Whakapapa

For our project, `Pūkenga` and `Whakapapa` are reflected in the idea that technical work
should be grounded in understanding, responsibility, and context. Handling user data is
not only a coding task. It also requires awareness of who the data relates to and how
system decisions affect real people.

This is reflected in design choices such as:

- being careful about what user data is collected and displayed
- treating privacy and access control as design decisions from the beginning
- making design choices based on likely user impact, not only technical convenience

### 2.2 Pono and Tika

Ideas such as `Pono` and `Tika` are reflected in the need for the platform to behave
fairly and honestly. Users should be able to trust that the system handles their
information properly and does not misrepresent what is public or private.

In practical terms, this means:

- passwords are stored as hashes rather than plain text
- public profile pages do not expose full private identity information
- users choose their preferred public contact method
- AI-generated listing drafts are shown as suggestions, not final decisions

### 2.3 Wānanga and Kaitiaki

`Wānanga` and `Kaitiaki` are reflected in the idea that data and platform activity
should be managed with care, discussion, and clear responsibility. Once the platform
stores data, it needs rules about who can access it, who can change it, and who is
responsible for moderation decisions.

In this project, this is reflected by:

- separating visitor, user, and administrator roles
- protecting routes that should not be public
- limiting administrator actions to moderation-related responsibilities
- keeping public and private profile data separate

### 2.4 Wairua and Mauri

`Wairua` and `Mauri` are most relevant in the way we try to keep the system respectful
and proportionate. We did not want the platform to collect more data or introduce more
complexity than the marketplace workflow actually needed.

Examples include:

- collecting only the data needed for registration and communication
- allowing users to control what contact detail becomes public
- keeping the request-based transaction flow simple rather than expanding into a larger
  checkout system

### 2.5 Tapu and Noa

`Tapu` and `Noa` can be understood here as balancing openness and protection. A
marketplace needs enough visibility for browsing and communication, but it should not
expose more user data than necessary.

This is reflected by:

- allowing public listing browsing without login
- limiting personal profile exposure
- restricting protected actions to authorised users only

## 3. Māori Data Sovereignty Across the Project Lifecycle

Māori Data Sovereignty highlights rights and interests in the collection, ownership, and
use of data. Our project is not a dedicated Māori data platform, but the idea is still
relevant because it reminds us that user data should not be treated as something the
system can simply take and use without limits. It should be handled with care, clear
purpose, and appropriate control.

### 3.1 Planning and Design

At the planning stage, we considered which user information should stay private and which
could be shown publicly. We also treated privacy, role separation, and data visibility as
design issues from the start rather than as later fixes.

### 3.2 Development and Implementation

During development, these ideas were applied through password hashing, role-based access
control, contact preference settings, and limits on what public profiles display. They
also influenced smaller design decisions, such as hiding management-only actions from
normal users and keeping admin features separate from marketplace participation.

### 3.3 Deployment and Storage

As the project moves toward deployment, the same ideas still apply. If images or other
user data are stored in cloud services such as Amazon S3, access control, privacy, and
credential handling still need to be managed carefully. In other words, responsible data
handling should continue beyond coding and into deployment decisions as well.

## 4. Conclusion

We do not claim that this student project fully implements Māori data governance at a
production level. However, we do believe these principles are relevant to the project
and useful for making better design decisions. In our case, they are reflected mainly in
how we handle privacy, user control, visibility of personal data, and responsibility for
platform actions across the project lifecycle.
