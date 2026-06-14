# Development Guidelines

## 1. Purpose

This document defines the mandatory development rules for the `Second-Hand Trading Platform` project.

Both developers must follow this document when writing code, naming files and fields, structuring logic, defining routes, updating the database, and integrating features.

These rules apply to:

- backend code
- frontend templates
- database-related code
- AI-related code
- recommendation-related code
- administrator-related code
- refactoring work

## 2. Program Style Rules

### Core Rules

| Rule | Definition |
|---|---|
| Correctness | Code correctness has priority over speed. |
| Readability | Readability has priority over clever or compact code. |
| Shared understanding | Every new function, route, and template must be understandable by the other developer without verbal explanation. |
| Temporary code | Temporary code must follow the same readability rules as permanent code. |

### Layout Rules

| Rule | Definition |
|---|---|
| Indentation | Use 4 spaces for indentation. |
| Line length | Keep each line within 100 characters. |
| Blank lines | Use blank lines to separate logical sections. |
| Nesting | No function may exceed 4 levels of indentation. |
| Single-line actions | Do not place multiple unrelated actions on the same line. |

### Function Rules

| Rule | Definition |
|---|---|
| Single responsibility | Every function must have one clear responsibility. |
| Function length | No function may exceed 30 lines, including comments and blank lines, unless both developers explicitly agree that splitting it would reduce clarity. |
| Repeated logic | Logic repeated in 2 or more places must be extracted into a reusable helper or service function. |
| Duplication | Copy-and-paste duplication is not allowed when the duplicated block can be named and extracted cleanly. |
| Return functions | Functions that return a value must not print output unless printing is the explicit purpose of that function. |
| Route size | Route handlers must not contain large blocks of business logic. |

### Documentation Rules

| Rule | Definition |
|---|---|
| File docstring | Every non-trivial Python file must include a short file-level docstring. |
| Function docstring | Every non-trivial function must include a short docstring describing its purpose. |
| Comment purpose | Comments must explain purpose, reasoning, or business rules. |
| Comment restriction | Comments must not restate obvious syntax. |

## 3. Functional Decomposition Rules

### Mandatory Decomposition Rules

- Each route must handle request input and response output only.
- Business logic must be placed in helper functions or service functions.
- Database update logic must not be repeated across multiple routes.
- AI listing draft logic must be isolated from standard listing form handling.
- Homepage recommendation logic must be isolated from listing browse page rendering.
- Admin control logic must be isolated from normal user route logic.

### Function Extraction Rules

A code block must be extracted into a function when any of the following is true:

- the code block has a clear nameable role
- the logic appears more than once
- the current function mixes validation, database updates, and page rendering
- the current function becomes too long
- the current function becomes difficult to test or explain

### Route Decomposition Rules

Each route function must be limited to these tasks:

- receive request data
- check login or role requirements
- validate required input
- call one or more support functions
- return a template or redirect

Route functions must not contain:

- repeated SQL or repeated ORM logic
- recommendation ranking logic
- AI response parsing logic
- complex multi-step transaction state logic

## 4. Naming Conventions

Naming is fixed across the project. The same concept must use the same name everywhere.

### Python and Database Naming

| Item | Required Format |
|---|---|
| Python files | `snake_case.py` |
| Variables | `snake_case` |
| Functions | `snake_case` |
| Classes | `PascalCase` |
| Constants | `UPPER_CASE` |
| Table names | plural `snake_case` |
| Column names | `snake_case` |
| Foreign keys | `<entity>_id` |
| Time fields | `created_at`, `updated_at` |

### Template Naming

| Item | Required Format |
|---|---|
| Template files | `snake_case.html` |
| CSS files | `snake_case.css` |
| Reusable partials | leading underscore names such as `_listing_card.html` |

### Route Naming

- Route paths must be lowercase.
- Route paths must be meaningful.
- Route paths such as `/do_action`, `/temp`, or `/page1` are not allowed.

Approved examples:

- `/login`
- `/register`
- `/listings`
- `/listings/<id>`
- `/favorites`
- `/requests`
- `/admin/users`

### Fixed Project Terms

| Allowed Term | Not Allowed |
|---|---|
| `favorite_list` | `wishlist`, `favourite_list`, `fav_list` |
| `listing` | alternative product names used inconsistently |
| `request` | inconsistent replacement terms |
| `transaction` | inconsistent replacement terms |
| `preferred_contact_method` | shortened or renamed variants |
| `administrator` | inconsistent admin naming |
| `user` | `customer`, `member` |
| `visitor` | inconsistent public-user naming |

## 5. Status and Business Rule Conventions

### Listing Status

Only these listing status values are allowed:

- `available`
- `pending`
- `sold`

### Request Status

Only these request status values are allowed:

- `pending`
- `accepted`
- `rejected`
- `completed`

### Mandatory Business Rules

- Sold listings must not appear in normal available-item browse or search results.
- Only the seller may edit or delete their own listing.
- Only completed transactions may receive reviews.
- Age verification must run automatically during registration.
- The administrator may view, delete, and lock.
- The administrator must not accept, reject, complete, or otherwise decide a buyer-seller transaction on behalf of users.

## 6. Flask Project Structure

### Required Structure

| Location | Required Use |
|---|---|
| `app.py` or `main.py` | app startup and app configuration only |
| `routes/` | Flask route handlers only |
| `models/` | database models and schema-related code only |
| `services/` | business logic only |
| `templates/` | HTML templates only |
| `static/` | CSS, JavaScript, and image assets only |
| `utils/` | small helper functions only |

### Structure Rules

- Startup code must stay in `app.py` or `main.py`.
- Route handlers must stay in the route layer.
- Business logic must stay in services or helper modules.
- Templates must not contain complex business logic.
- Templates must not query the database directly.
- AI listing draft logic must be placed in a dedicated AI-related service module.
- Homepage recommendation logic must be placed in a dedicated recommendation-related service module.
- Admin routes must be separated from normal user routes.

## 7. API Contract Reference

The shared route contract is defined in:

- [API_Specification.md](/Users/fanfan/Documents/GitHub/MSE800-Assessment2/doc/API_Specification.md)

Both developers must follow that document when implementing:

- route paths
- form fields
- request and response structure
- redirects
- status changes
- AI listing draft integration
- homepage recommendation integration
- administrator control actions

## 8. Frontend and Template Rules

### Required Page Rules

- All main pages must include a consistent top navigation area.
- All form pages must use a consistent layout.
- All similar forms must use the same field order where the same fields appear.
- All validation errors must appear clearly on the page.
- All status labels must use the exact approved status words.

### Required Listing Display Rules

Every listing card must display:

- image
- title
- price
- condition
- status

### Required Profile Display Rules

Every public profile page must display:

- display name
- preferred contact method
- selected public contact detail if available

When trust indicators are implemented in the later trust sprint, every public profile page must also display:

- trust indicators

### Required UI Consistency Rules

The following must stay consistent across templates:

- button labels
- form labels
- request status wording
- administrator action wording
- favorite list wording

## 9. Git and Collaboration Rules

### Branch Rules

- Each branch must contain one main feature group or one bug-fix group.
- Branch names must be descriptive.
- Branch names must use one of these prefixes:
  - `feature/`
  - `fix/`
  - `refactor/`
  - `docs/`

Approved examples:

- `feature/login`
- `feature/listing-crud`
- `feature/ai-listing-draft`
- `feature/homepage-recommendation`
- `fix/request-status-bug`

### Commit Rules

- Every commit message must be short and meaningful.
- Every commit message must use one of these prefixes:
  - `feat:`
  - `fix:`
  - `refactor:`
  - `docs:`

Approved examples:

- `feat: add listing creation form`
- `fix: correct sold status update`
- `refactor: move request logic into service`
- `docs: update system design`

### Collaboration Rules

- Both developers must pull the latest main branch before starting a new work session.
- Shared field names must not be changed without agreement from both developers.
- Shared route names must not be changed without agreement from both developers.
- Database schema changes must be discussed before implementation.
- AI route changes must be communicated before frontend integration.
- Recommendation data changes must be communicated before frontend integration.
- At the end of each sprint, both developers must test the integrated version together.

## 10. Testing and Verification Rules

### Minimum Testing Rules

Every implemented feature must be tested manually before it is marked complete.

The following flows must be tested whenever relevant code is changed:

- registration and login
- listing creation, editing, and deletion
- browse, search, and filters
- favorite list add and view
- purchase request submission
- request accept, reject, and complete actions
- sold status update
- review submission
- AI listing draft generation
- homepage recommendation display
- administrator deletion and locking actions

### Bug Fix Rules

- Every bug fix must include retesting the original failure path.
- Every bug fix must include one related workflow check.

## 11. Definition of Done for Development Work

A task is complete only when all of the following are true:

- the code works correctly
- the code follows this naming and style guide
- the logic is split into sensible functions
- repeated logic has been removed or extracted into shared functions
- required database changes are complete
- the feature is integrated into the correct workflow
- the feature has been tested manually
- the code has been committed with a clear commit message

## 12. Project-Specific Feature Boundaries

### AI One-Click Listing Assistant

- Use one listing image only.
- Generate a draft only.
- Use internal platform listing data for rough price reference only.
- Do not use external market price integration.
- Do not implement multi-image AI recognition.

### Homepage Recommendation

- Use lightweight internal logic only.
- Use search, browsing, and favorite list behaviour only.
- Do not implement heavy machine learning pipelines.
- Do not use vector databases.
- Do not use advanced semantic search infrastructure.

### Admin Controls

The administrator may:

- view user accounts
- view listings
- delete inappropriate listings
- view request records
- view completed request records
- lock user accounts
- lock request records

The administrator must not:

- accept purchase requests on behalf of users
- reject purchase requests on behalf of users
- confirm transactions on behalf of users
- change the final buyer-seller transaction outcome directly
