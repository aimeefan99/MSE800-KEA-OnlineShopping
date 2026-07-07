# API Specification

## 1. Purpose

This document defines the shared route, request field, and response behaviour for the `Second-Hand Trading Platform` project.

Both developers must follow this document when implementing:

- form fields
- route handlers
- redirects
- status updates
- AI listing draft integration
- homepage recommendation integration
- administrator actions

If a shared route, field name, or response structure must change, both developers must agree before implementation.

## 2. Global Rules

### Route Method Rules

| Action Type | Required Method |
|---|---|
| View page | `GET` |
| Read page data | `GET` |
| Create record | `POST` |
| Update record | `POST` |
| Delete record | `POST` |
| Change status | `POST` |
| Admin control action | `POST` |

### Shared Response Rules

- Successful form submission must redirect.
- Validation failure must return a visible error message on the page.
- Required input must be checked before database write.
- Shared field names must stay identical across forms, routes, templates, and database logic.

### Fixed Shared Field Names

| Field | Meaning |
|---|---|
| `display_name` | public profile name |
| `full_name` | full personal name |
| `date_of_birth` | registration age check field |
| `email` | login email |
| `phone_number` | phone contact field |
| `preferred_contact_method` | public contact preference |
| `bio` | short profile description |
| `title` | listing title |
| `description` | listing description |
| `condition` | listing condition |
| `price` | listing price |
| `image` | uploaded listing image |
| `category_id` | selected category id |
| `listing_id` | target listing id |
| `buyer_id` | buyer user id |
| `seller_id` | seller user id |
| `request_id` | purchase request id |
| `score` | review rating value |
| `comment` | review text |
| `price_reference` | AI draft rough price result |
| `status` | listing or request status |
| `category` | AI draft suggested category label |

## 3. Authentication Routes

### Register

| Item | Definition |
|---|---|
| Route | `POST /register` |
| Required fields | `display_name`, `full_name`, `date_of_birth`, `email`, `password`, `preferred_contact_method` |
| Optional fields | `phone_number` |
| Success result | create user account and redirect to login or home page |
| Failure result | show validation error on register page |

Validation rules:

- `email` must be unique.
- `date_of_birth` must pass age verification.
- `preferred_contact_method` must be `email` or `phone`.
- if `preferred_contact_method` is `phone`, `phone_number` must be provided.

### Login

| Item | Definition |
|---|---|
| Route | `POST /login` |
| Required fields | `email`, `password` |
| Success result | create login session and redirect |
| Failure result | show error message on login page |

### Logout

| Item | Definition |
|---|---|
| Route | `POST /logout` |
| Required fields | none |
| Success result | clear session and redirect |

## 4. Listing Routes

### Create Listing

| Item | Definition |
|---|---|
| Route | `POST /listings/create` |
| Required fields | `title`, `category_id`, `description`, `condition`, `price`, `image` |
| Success result | create listing with `available` status |
| Owner rule | listing belongs to the logged-in user |

Rules:

- manual form submission and AI-prefilled submission use the same final create route
- the final saved listing must come from user-confirmed values only
- `category_id` must match an existing category

### Edit Listing

| Item | Definition |
|---|---|
| Route | `POST /listings/<listing_id>/edit` |
| Required fields | `title`, `category_id`, `description`, `condition`, `price` |
| Optional fields | `image` |
| Success result | update listing and redirect to listing page or listing management page |
| Owner rule | only the seller may edit the listing |

### Delete Listing

| Item | Definition |
|---|---|
| Route | `POST /listings/<listing_id>/delete` |
| Required route parameter | `listing_id` |
| Success result | remove seller-owned listing and redirect |
| Owner rule | only the seller may delete the listing |

### View Listing Detail

| Item | Definition |
|---|---|
| Route | `GET /listings/<listing_id>` |
| Required route parameter | `listing_id` |
| Required page data | image, title, price, condition, status, description, seller username, available contact method |

### Browse Listings

| Item | Definition |
|---|---|
| Route | `GET /listings` |
| Supported query fields | `keyword`, `category_id`, `condition`, `min_price`, `max_price` |
| Result rule | sold listings must not appear in normal available-item results |

## 5. Favorite List Routes

### Add to Favorite List

| Item | Definition |
|---|---|
| Route | `POST /favorites/add` |
| Required fields | `listing_id` |
| Success result | save listing to the current user's favorite list |

Rules:

- the same user cannot save the same listing more than once
- if the listing is already saved, the system keeps one saved record only

### Remove from Favorite List

| Item | Definition |
|---|---|
| Route | `POST /favorites/remove` |
| Required fields | `listing_id` |
| Success result | remove listing from the current user's favorite list |

### View Favorite List

| Item | Definition |
|---|---|
| Route | `GET /favorites` |
| Required data | saved listings for the logged-in user |

## 6. Purchase Request and Transaction Routes

### Submit Purchase Request

| Item | Definition |
|---|---|
| Route | `POST /requests/create` |
| Required fields | `listing_id` |
| Optional fields | `message` |
| Success result | create request with `pending` status |

Rules:

- `buyer_id` and `seller_id` must be stored correctly
- a user cannot submit a request on their own listing
- only listings with `available` status can accept a new request
- sold listings and pending listings must not accept a new request

### Accept Request

| Item | Definition |
|---|---|
| Route | `POST /requests/<request_id>/accept` |
| Required route parameter | `request_id` |
| Success result | update request status to `accepted` and update related listing status to `pending` |
| Owner rule | only the listing owner may accept the request |

Rules:

- only one request per listing can be accepted
- when one request is accepted, other open requests for the same listing remain pending until the listing is marked sold or the accepted request is rejected

### Reject Request

| Item | Definition |
|---|---|
| Route | `POST /requests/<request_id>/reject` |
| Required route parameter | `request_id` |
| Success result | update request status to `rejected` |
| Owner rule | only the listing owner may reject the request |

Rules:

- if the rejected request was the accepted request for that listing, the related listing returns to `available`

### Complete Transaction

| Item | Definition |
|---|---|
| Route | `POST /requests/<request_id>/complete` |
| Required route parameter | `request_id` |
| Success result | update request status to `completed` and update related listing status to `sold` |
| Owner rule | only the buyer of the accepted request may complete the transaction |

Rules:

- only an `accepted` request can be completed
- when a listing is marked `sold`, all remaining open requests for that listing are closed or rejected

### View Incoming Requests

| Item | Definition |
|---|---|
| Route | `GET /requests/incoming` |
| Required data | requests on listings owned by the logged-in user |

### View Request and Transaction History

| Item | Definition |
|---|---|
| Route | `GET /requests/history` |
| Required data | request records involving the logged-in user, including completed requests used as transaction history |

## 7. Review Routes

### Create Review

| Item | Definition |
|---|---|
| Route | `POST /reviews/create` |
| Required fields | `request_id`, `reviewed_user_id`, `score` |
| Optional fields | `comment` |
| Success result | create one review record and redirect |

Rules:

- only a completed request can be reviewed
- one user can review the other party once per completed request at most
- `score` must be an integer from `1` to `5`
- the reviewer must be either the buyer or seller of the related request
- `reviewed_user_id` must be the other party in the related request

## 8. AI Listing Draft Route

### Generate Listing Draft

| Item | Definition |
|---|---|
| Route | `POST /ai/listing-draft` |
| Required fields | `image` |
| Required output fields | `title`, `category`, `description`, `price_reference` |

Rules:

- the response is a draft only
- the route must not create a final listing record
- the user must review and confirm the final values before publishing
- `category` is a suggested category label and must be mapped to a valid `category_id` before final listing creation
- `price_reference` is a rough result based on internal listing data only and is not stored as a standalone database field in the first version
- multi-image AI recognition is out of scope
- external market price integration is out of scope

Example output structure:

```json
{
  "title": "Dell 24-inch Monitor",
  "category": "Electronics",
  "description": "Used monitor in good condition with power cable included.",
  "price_reference": 120
}
```

## 9. Homepage Recommendation Route

### Homepage Recommendation

| Item | Definition |
|---|---|
| Route | `GET /recommendations/homepage` |
| Internal inputs | recent search behaviour, recent browsing behaviour, recent favorite list behaviour |
| Required output | prioritised listings |

Rules:

- the feature returns listing results only
- the feature does not expose technical scoring metadata to templates
- the feature uses lightweight internal logic only
- request behaviour is not part of the recommendation logic

## 10. Public Profile Routes

### View Public Profile

| Item | Definition |
|---|---|
| Route | `GET /profiles/<user_id>` |
| Required route parameter | `user_id` |
| Required page data | `display_name`, completed transaction count, average rating or positive feedback rate, review summary, preferred contact method, selected public contact detail, optional bio |

### Edit Profile

| Item | Definition |
|---|---|
| Route | `POST /profile/edit` |
| Editable fields | `display_name`, `full_name`, `phone_number`, `preferred_contact_method`, `bio` |
| Owner rule | users may edit only their own profile |

Rules:

- if `preferred_contact_method` is `phone`, `phone_number` must be provided

## 11. Admin Routes

### View Users

| Item | Definition |
|---|---|
| Route | `GET /admin/users` |
| Access rule | administrator only |

### View Listings

| Item | Definition |
|---|---|
| Route | `GET /admin/listings` |
| Access rule | administrator only |

### Delete Inappropriate Listing

| Item | Definition |
|---|---|
| Route | `POST /admin/listings/<listing_id>/delete` |
| Access rule | administrator only |
| Effect | delete inappropriate listing |

### View Request Records

| Item | Definition |
|---|---|
| Route | `GET /admin/requests` |
| Access rule | administrator only |

### View Completed Transaction Records

| Item | Definition |
|---|---|
| Route | `GET /admin/requests/completed` |
| Access rule | administrator only |
| Data source | completed `requests` records, not a separate `transactions` table |

### Lock User Account

| Item | Definition |
|---|---|
| Route | `POST /admin/users/<user_id>/lock` |
| Access rule | administrator only |
| Effect | prevent normal platform actions for that user |

### Lock Request Record

| Item | Definition |
|---|---|
| Route | `POST /admin/requests/<request_id>/lock` |
| Access rule | administrator only |
| Effect | freeze the target request record for review |

### Unlock Request Record

| Item | Definition |
|---|---|
| Route | `POST /admin/requests/<request_id>/unlock` |
| Access rule | administrator only |
| Effect | reopen a locked request record for normal review flow |

Rules:

- in the first version, transaction records are represented by completed `requests` records rather than a separate `transactions` table
- the administrator may view, delete, lock, and unlock
- the administrator must not accept, reject, or complete buyer-seller transactions on behalf of users
