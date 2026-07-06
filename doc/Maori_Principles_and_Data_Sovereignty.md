# Māori Principles and Data Sovereignty

## 1. Introduction

This report explains how Māori principles and Māori Data Sovereignty are considered in
the `Second-Hand Trading Platform` project. Software development is not only about
building features. It also includes making responsible decisions about how data is
collected, stored, used, and shared.

In our project, that includes user account data, profile information, contact details,
listing images, request records, and AI-assisted content generation. These ideas are
considered in a practical way throughout the project lifecycle.

## 2. Why Māori Principles Matter in This Project

This platform handles personal and user-generated data. Because of that, it is important
to think about privacy, trust, transparency, and responsible data handling from the
start. Māori principles are useful in this project because they push us to think about
data as something connected to people, control, and responsibility, not just as
something to store in the database.

These principles are relevant here because the system includes:

- user registration details
- public and private profile information
- uploaded product images
- request and transaction records
- administrator moderation features
- AI-assisted listing suggestions

This means the platform should not treat data as only something technical. It should also
be handled with clear purpose, appropriate control, and respect for the people behind
the data.

## 3. Māori Principles Considered in the Project

### 3.1 Pūkenga and Whakapapa

`Pūkenga` and `Whakapapa` are mainly reflected here in how we approach design
responsibly. We understand that handling user data is not only a coding task. It also
requires awareness of who the data belongs to and how system decisions may affect users.

This is reflected in design choices such as:

- considering cultural and ethical issues rather than only technical convenience
- being careful about what user data is collected and displayed
- treating data-related decisions as part of design responsibility

### 3.2 Pono and Tika

`Pono` and `Tika` are most visible in the way we try to protect user trust. If users
give information to the platform, they should be able to trust that it is handled in a
fair and sensible way.

Examples include:

- passwords are stored as hashes rather than plain text
- public profile pages do not expose full private identity information
- users control their preferred contact method
- AI-generated listing drafts are presented as suggestions, not as final truth

These choices help make the platform more trustworthy and reduce inappropriate use of
data.

### 3.3 Wānanga and Kaitiaki

`Wānanga` and `Kaitiaki` are reflected in how we think about responsibility around data.
Once the platform stores user and listing data, it needs clear rules for who can access
what and who is allowed to act on it.

Examples include:

- the system separates normal user actions from administrator actions
- access control is applied to protected routes
- administrator actions are limited to moderation-related responsibilities
- uploaded images and listing records are managed as structured platform data

Storing data also means taking responsibility for how it is used and protected.

### 3.4 Wairua and Mauri

`Wairua` and `Mauri` are reflected in the idea that the system should collect and use
data for clear reasons. We did not want to collect information that had no practical
role in the marketplace workflow.

This is reflected by:

- collecting only the user information needed for registration and communication
- using profile settings to control what becomes public
- keeping the request-based marketplace flow simple and understandable
- using AI to assist listing creation rather than replacing user control

This helps keep the platform purposeful rather than collecting or sharing information
without a clear reason.

### 3.5 Tapu and Noa

`Tapu` and `Noa` can be understood here as balancing openness and protection.
A trading platform needs enough visibility for browsing and communication, but it should
not expose more user data than necessary.

In our project, this balance is reflected by:

- allowing public listing browsing without exposing full private user data
- showing seller contact information according to chosen contact preferences
- limiting protected actions to logged-in and authorised users
- treating storage and deployment decisions as part of data risk management

## 4. Māori Data Sovereignty Across the Project Lifecycle

Māori Data Sovereignty refers to the rights and interests Māori have in relation to the
collection, ownership, and application of Māori data. In this project, that idea
encourages careful thinking about ownership, control, and responsible use of data
throughout the project lifecycle.

### 4.1 Planning and Design

At the planning stage, we tried to avoid unnecessary data collection. We considered which
user details needed to remain private and which could be shown publicly as part of the
marketplace workflow.

This included:

- separating public profile data from private account data
- defining roles clearly for visitors, users, and administrators
- treating privacy and access control as design concerns from the beginning

### 4.2 Development and Implementation

During development, these ideas were applied in practical ways:

- password hashing is used during authentication
- protected actions require login and correct role access
- preferred contact method controls what contact detail is shown publicly
- administrator access is separated from buyer and seller actions

These decisions help make data handling more controlled and more accountable.

### 4.3 AI and Data Use

The project includes AI-assisted listing generation, so data use is also important in the
AI feature. Uploaded product images and generated listing drafts should be treated
carefully because they are still part of user-controlled content.

In this project:

- AI output is used to assist the user, not to make the final decision automatically
- the user reviews and edits the generated draft before publishing
- generated content is treated as a suggestion, not as an unquestionable result

This supports transparency and keeps users in control of their own listing content.

### 4.4 Storage and Deployment

As the project moves toward deployment planning, these issues still matter. If listing
images are stored in cloud services such as Amazon S3, those decisions should still
respect privacy, access control, and careful handling of user data.

For this reason, deployment planning should continue to consider:

- who can access stored data
- how user-uploaded content is protected
- how sensitive configuration and credentials are managed

## 5. Practical Commitments in This Project

Based on the principles above, the project makes the following practical commitments:

- collect only data needed for the platform to function
- protect passwords and sensitive user information
- avoid exposing more profile data than necessary
- keep users in control of final listing content
- apply access control to user and administrator actions
- treat uploaded images and generated data responsibly
- continue considering data governance when deployment choices are made

## 6. Conclusion

In this project, these ideas are applied through practical decisions about privacy, user
control, public data visibility, and respectful interface design.

By thinking about privacy, trust, purpose, and data control from planning through to
implementation and deployment planning, we aimed to treat user data as something that
deserves care and responsibility, not just as a technical resource.
