from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from decimal import Decimal
from uuid import UUID


from .pagination import Pagination

class DocumentId(BaseModel):
    id: UUID = Field(..., description="DB ID of Document table")
    
class DocumentBaseModel(DocumentId):
    """Schema for getting a prompt Base."""
    name: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=255, 
        description="Document name."
    )
    latest_revision_id: Optional[UUID] = Field(None, description="This represents the latest saved data")
    status: int = Field(..., ge=1, description="Status which mentions its waiting for AI editing or manually editing or finished")
    category_id: int = Field(..., ge=1, description='Represent document category table id')
    category_name: str = Field(..., description='Represent document category label')
    updated_at: str = Field(..., description="When the user was last modified")
    is_uploaded: Optional[bool] = Field(
        None, 
        description="This status indicated whether its uploaded file or created from here."
    )


class PaginatedDocumentResponse(BaseModel):
    data: List[DocumentBaseModel] = Field(..., description="Documents details")
    pagination: Pagination = Field(..., description="Pagination details")
    
    class Config:
        from_attributes = True

class SingleDocumentDetail(DocumentBaseModel):
    content: str = Field(..., description="Always keeps latest changes")

class SingleDocumentWrapResponse(BaseModel):
    data: SingleDocumentDetail = Field(..., description="Keeps the result")
    
    class Config:
        from_attributes = True

class UpdateDocumentContent(BaseModel):
    content: str = Field(..., description="Always keeps latest changes")
    is_auto: bool = Field(..., description="Represents its manual save or auto submit")

class DocumentCreate(BaseModel):
    name: str = Field(..., description="Name the new document")
    content: str = Field(..., description="new document content")
    


class DocumentContentOnly(BaseModel):
    content: str = Field(
        ...,
        description="The result generated via AI or manually editted"
    )

class DocumentContentOnlyResponse(BaseModel):
    data: DocumentContentOnly

    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    data: DocumentId = Field(..., description="Documents details")
    message: str = Field(..., description="Responnse status as message")
    class Config:
        from_attributes = True

# class DiffCounts(BaseModel):
#     deleted: int = Field(..., description="Number of deleted segments")
#     inserted: int = Field(..., description="Number of inserted segments")
#     modified: int = Field(..., description="Number of modified segments")

# class DiffContent(BaseModel):
#     counts: DiffCounts = Field(..., description="Counts summary")
#     diff_html: str = Field(..., description="HTML (rich) diff produced by Redlines")


# class DiffData(BaseModel):
#     content: DiffContent = Field(..., description="Diff payload")


# class DiffResponse(BaseModel):
#     data: DiffData = Field(..., description="Wrapped response")

#     class Config:
#         from_attributes = True

class DocumentId(BaseModel):
    id: UUID = Field(..., description="The ID of the uploaded document")
