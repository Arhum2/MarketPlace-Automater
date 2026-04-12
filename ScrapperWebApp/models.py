from __future__ import annotations
import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

# Scrapped data
class ScrappedData(BaseModel):
    title: Optional[str]
    price: Optional[str]
    description: Optional[str]
    images: List[str]
    link: str

# User input - when scrapper fails
class UserInput(BaseModel):
    title: Optional[str] = None
    price: Optional[str] = None
    description: Optional[str] = None

# Job Status
class JobStatus(str, Enum):
    PENDING = "pending"           # Job just created
    SCRAPING = "scraping"         # Currently scraping
    WAITING_INPUT = "waiting_input"  # Scraping done, user needs to fill fields
    QUEUED = "queued"             # Ready to post to Facebook
    POSTING = "posting"           # Currently posting
    POSTED = "posted"             # Successfully posted ✅
    FAILED = "failed"             # Something went wrong ❌

# Job
class Job(BaseModel):
    job_id: str
    url: str
    status: JobStatus
    scraped_data: Optional[ScrappedData] = None
    missing_fields: List[str] = []
    user_data: Optional[UserInput] = None
    temp_folder: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime.datetime

# Product
class Product(BaseModel):
    url: str
    title: Optional[str] = None
    price: Optional[str] = None
    description: Optional[str] = None
    sold: Optional[bool] = False
    missing_fields: List[str] = []
    folder_path: Optional[str] = None
    scraped_at: Optional[datetime.datetime] = None
    posted_at: Optional[datetime.datetime] = None
    sold_at: Optional[datetime.datetime] = None

# Create Product Request
class CreateProductRequest(BaseModel):
    url: str

# Update Product Request
class UpdateProductRequest(BaseModel):
    title: Optional[str] = None
    price: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
