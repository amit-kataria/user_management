from pydantic import BaseModel, Field, EmailStr, BeforeValidator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from typing_extensions import Annotated

# Helper for ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]


class MongoRef(BaseModel):
    ref: str = Field(..., alias="$ref")
    id_obj: Dict[str, str] = Field(..., alias="$id")  # Expecting {"$oid": "..."}

    @staticmethod
    def from_id(collection: str, oid: str):
        return MongoRef(**{"$ref": collection, "$id": {"$oid": oid}})


class Permission(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    name: str
    description: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={datetime: lambda v: v.isoformat()},
    )


class Role(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    name: str
    description: Optional[str] = None
    isDefault: bool = False
    permissions: List[MongoRef] = []
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class User(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    firstName: str
    lastName: str
    gender: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    password: str  # Hashed
    enabled: bool = True
    confirmed: bool = False
    tenant: str
    timezone: Optional[str] = None
    role: Optional[MongoRef] = None
    permissions: List[MongoRef] = []
    attributes: Dict[str, Any] = {}
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    # Audit fields mentioned in audit requirement, usually on the document itself too?
    # "Each Document will have createdAt, updatedAt, createdBy, updatedBy and deletedAt."
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class AuditLog(BaseModel):
    action: str
    target_collection: str
    target_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    performed_by: str
    details: Dict[str, Any] = {}
