from pydantic import BaseModel

class SuperAdminLoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SuperAdminResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    
    # Profile & Address Data
    phone: str | None = None
    position: str | None = None
    location: str | None = None
    state: str | None = None
    pin: str | None = None
    zip: str | None = None
    tax_no: str | None = None
    
    # Social URLs
    facebook_url: str | None = None
    twitter_url: str | None = None
    github_url: str | None = None
    dribbble_url: str | None = None

    class Config:
        from_attributes = True


class SuperAdminUpdateRequest(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    position: str | None = None
    location: str | None = None
    state: str | None = None
    pin: str | None = None
    zip: str | None = None
    tax_no: str | None = None
    
    facebook_url: str | None = None
    twitter_url: str | None = None
    github_url: str | None = None
    dribbble_url: str | None = None
