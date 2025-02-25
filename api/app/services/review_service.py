from sqlalchemy.orm import Session
from app.repositories.review_repository import ReviewRepository
from .base_service import BaseService

class ReviewService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, ReviewRepository)