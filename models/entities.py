"""Core domain entities for the second-hand trading platform."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """Represent a platform user account."""

    display_name: str
    full_name: str
    date_of_birth: str
    email: str
    preferred_contact_method: str
    role: str = "user"
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    is_locked: bool = False
    id: Optional[int] = None


@dataclass
class Category:
    """Represent a listing category."""

    name: str
    id: Optional[int] = None


@dataclass
class Listing:
    """Represent a marketplace listing."""

    seller_id: int
    category_id: int
    title: str
    description: str
    condition: str
    price: float
    image_url: str
    status: str = "available"
    id: Optional[int] = None


@dataclass
class Request:
    """Represent a purchase request."""

    listing_id: int
    buyer_id: int
    seller_id: int
    status: str = "pending"
    message: Optional[str] = None
    is_locked: bool = False
    id: Optional[int] = None


@dataclass
class Review:
    """Represent a review left after a completed transaction."""

    request_id: int
    reviewer_id: int
    reviewed_user_id: int
    score: int
    comment: Optional[str] = None
    id: Optional[int] = None
