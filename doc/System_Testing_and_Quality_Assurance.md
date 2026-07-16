# System Testing and Quality Assurance

## 1. Purpose

This document explains how the `Second-Hand Trading Platform - Kea Marketplace` project is tested and how
verification and validation are used to show that the implemented system meets its
intended requirements and user goals.

The functional and non-functional requirements referenced in this document are defined in
`Project_Requirements.md`. This document does not repeat the full requirements list.
Instead, it focuses on the testing strategy, verification approach, validation approach,
and supporting evidence used to assess those requirements.

It combines:

- the overall testing strategy
- the verification approach against documented requirements
- the validation approach against intended user needs
- the evidence used to support testing and final evaluation

## 2. Testing Strategy

This project uses a practical testing strategy suitable for a two-person software
project. The aim is not only to check whether individual features work, but
also to confirm that the whole platform behaves correctly as an integrated second-hand
trading system.

The strategy follows standard software testing ideas in which testing is treated as the
main verification activity and product readiness is linked to whether the system is:

- correct
- reliable
- safe
- robust

For this project, that means testing is used to:

- check that core workflows behave as specified
- catch defects early at route, service, and database level
- make sure protected actions are only available to the correct user role
- confirm that status changes such as `available`, `pending`, `sold`, `accepted`, and
  `completed` happen correctly
- protect important shared flows from regression when code is merged or refactored

The strategy combines manual browser testing and lightweight automated testing. This is
appropriate for the project because the system has many visible user workflows that need
to be checked in the browser, but it also has several shared platform rules that are
easy to break during parallel development and therefore benefit from automated smoke
tests.

Testing was not treated as a final-stage activity only. In line with the verification
and validation approach used in this project, testing started during implementation and
continued as features were integrated across sprints.

## 3. Testing Scope

Testing in this project covers the following areas:

- public browsing features
- user account features
- listing creation and management
- favorites
- request and transaction workflows
- public and private profile features
- administrator features
- AI-assisted listing draft generation
- interest-based homepage recommendation

The scope includes both functional and non-functional checking.

Functional testing focuses on whether the platform does what it is supposed to do, such
as registration, listing creation, request submission, seller response actions, and
administrator controls.

Non-functional checking focuses on whether the implemented system behaves in an acceptable
way for a prototype, such as:

- access control on protected routes
- password hashing
- stable page loading under normal demo conditions
- handling invalid form input without server crashes
- keeping the code structure maintainable for team development

## 4. Testing Levels and Methods

### 4.1 Unit Testing

Unit testing focuses on individual logic units such as helper functions or service-layer
behaviour. In this project, unit-level checking is most relevant for small business rules
that can be tested without going through the full browser flow.

Examples include:

- listing validation rules
- condition and status handling
- favorite duplication checks
- request status transition rules
- image path resolution helpers

Because this project uses a service-based structure, unit-level logic mainly sits in the
service and utility layers rather than in templates.

### 4.2 Subsystem Testing

Subsystem testing checks that related parts within one feature area work together
correctly, such as route handling, service logic, and database updates.

In this project, subsystem testing is important because many features are not just single
functions. They depend on several parts working together. For example:

- the register subsystem includes form input, validation, password hashing, database
  insertion, and redirect behaviour
- the listing subsystem includes create, edit, delete, image upload, and public display
- the transaction subsystem includes request creation, seller response actions, buyer
  completion, and listing status updates
- the admin subsystem includes role checks, management pages, and moderation actions

This level is useful for checking feature integration before looking at the full platform
end-to-end.

### 4.3 System Testing

System testing checks complete end-to-end workflows across the platform, such as browsing
items, creating listings, submitting requests, and completing transactions.

For this project, system testing includes full user journeys such as:

- a visitor browsing listings and opening item detail pages without logging in
- a new user registering and then logging in
- a seller creating a listing and checking that it appears in browse results
- a buyer saving a listing to favorites and reopening it later
- a buyer submitting a request, a seller responding to it, and the buyer completing the
  transaction
- an administrator opening management pages and moderating listings

This level is especially important because the project is built around connected
marketplace workflows rather than isolated pages.

### 4.4 Acceptance Testing

Acceptance testing checks whether the final system is suitable for demonstration and
matches the intended user workflows described in the project requirements.

Acceptance testing is the closest level to final user and stakeholder judgement. In this
project, acceptance testing is based on the
implemented user stories and their acceptance criteria.

Examples include confirming that:

- visitors can browse listings without registering
- sold listings do not appear in normal browsing results
- users can create listings with one image
- buyers can submit and track requests
- sellers can manage requests on their own listings
- administrators can access management functions while normal users cannot

This is the level most closely connected to final demonstration readiness.

### 4.5 Manual Testing

Manual testing is used for page rendering, form submission behaviour, navigation, and
user workflow validation in the browser.

Manual testing is important in this project because many marks depend on visible page
behaviour and realistic user interaction. It is used to check:

- page layout and navigation
- button visibility by role
- form validation messages
- redirect behaviour after successful or failed actions
- listing images and detail display
- request and admin flows from the user’s point of view

### 4.6 Automated Smoke Testing

Automated smoke testing is used to protect the most important platform rules and detect
major regressions quickly.

This project includes a smoke test file that checks a small set of critical shared rules.
This is especially useful because the codebase was developed in parallel by two team
members, which increases the chance of accidental regression in shared features.

The smoke tests focus on high-risk platform rules such as:

- admin accounts must not enter marketplace-only pages
- marketplace users must not access admin pages
- locked users must not continue using protected pages
- sold listings must stay out of public browsing results
- the same listing must not be saved twice by the same user
- public profiles must not expose private full-name data

### 4.7 Regression Testing

Regression testing is used after feature changes, merges, and refactoring to make sure
that earlier working behaviour has not been broken.

This was particularly important in this project because:

- multiple sprints changed shared templates and shared routes
- request and admin features depended on role logic
- image handling was reused across browse, detail, and favorites pages
- database-backed flows could be affected by small changes in service logic

In practice, regression testing was done by rerunning smoke tests and manually checking
the main workflows after significant code changes.

### 4.8 Product Readiness

Testing is closely linked to product readiness. For this project, the system is
considered ready for final demonstration when there is enough evidence to argue that the
prototype is dependable for its intended scope.

For this project, that means:

- core workflows are implemented and testable
- major defects in browsing, account access, listing management, and request flow are
  resolved
- role-based access rules are working
- core requirements have supporting verification evidence
- the system can be demonstrated through realistic user scenarios

## 5. Verification

Verification answers the question:

**Are we building the product right?**

In this project, verification is treated as proving that the software conforms to its
specified functional and non-functional requirements. That means
checking whether the implemented platform matches the documented requirements in
`Project_Requirements.md`, the expected route behaviour, and the intended system rules.

Verification in this project includes checking:

- whether the implemented routes behave as specified
- whether protected actions are correctly restricted by login, ownership, or role
- whether database updates follow the expected workflow rules
- whether feature behaviour matches user story acceptance criteria
- whether non-functional rules such as hashed passwords and public-page access are
  satisfied

Verification evidence may include:

- route and workflow checks
- screenshots of implemented pages
- automated smoke test results
- database state checks
- code inspection against documented requirements

This means verification is mostly requirement-based and implementation-based. It is less
about personal opinion and more about whether the system can be shown to conform to what
was specified.

## 6. Validation

Validation answers the question:

**Are we building the right product?**

In this project, validation means checking whether the delivered system makes sense as a
second-hand marketplace
prototype and whether the completed workflows are meaningful from the user point of view.

Validation is considered from these perspectives:

- visitor
- buyer
- seller
- administrator

The validation focus is whether the final platform supports realistic browsing, listing,
request, moderation, and discovery behaviour for the chosen scope.

Examples of validation in this project include checking whether:

- a visitor can explore the platform before deciding to register
- a seller can create a listing without unnecessary complexity
- a buyer can discover, save, and request items in a realistic way
- the request-based transaction flow is understandable for both buyer and seller
- the administrator role supports moderation without becoming part of the trading flow
- the AI-assisted listing feature and recommendation feature feel useful at prototype
  level rather than being only technical add-ons

Validation therefore focuses more on usefulness, suitability, and fitness for purpose
than on strict conformance to written specifications.

## 7. Evidence Against Requirements

This section should map project requirements to the evidence used to verify and validate
them.

Suggested table structure:

| Requirement ID | Requirement Summary | Verification Method | Validation Evidence | Result |
|---|---|---|---|---|
| FR-x / NFR-x | Short requirement summary | How the requirement was checked | User-facing evidence or workflow confirmation | Pass / Partial / Pending |

Examples of evidence that may be used:

- screenshots
- browser walkthroughs
- smoke test output
- database checks
- manual scenario testing
- code inspection against requirements

## 8. Limitations

This testing and V&V approach has some limitations:

- the project is a prototype, not a production-scale commercial system
- testing depth is limited by time and team size
- real payment integration is outside the project scope
- AI output may vary between runs
- performance and security testing are limited to the project level rather than full
  enterprise-level assessment

## 9. Conclusion

This document explains how testing, verification, and validation are applied to the
project in a way that matches both the documented quality approach and the actual system
implemented by the team.

Together, these sections support the claim that the project was not only built to work at
page level, but was also checked against documented requirements, realistic user
workflows, and prototype-level quality expectations.
