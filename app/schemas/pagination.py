from pydantic import BaseModel

class Pagination(BaseModel):
    current_page: int
    per_page: int
    length: int
    total: int
