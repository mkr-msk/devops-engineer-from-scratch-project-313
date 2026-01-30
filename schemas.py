from typing import Optional

from pydantic import BaseModel, HttpUrl, field_validator


class LinkCreate(BaseModel):
  original_url: HttpUrl
  short_name: str

  @field_validator('short_name')
  @classmethod
  def validate_short_name(cls, value: str) -> str:
    if not value or len(value.strip()) == 0:
      raise ValueError('short_name cannot be empty')
    if len(value) > 50:
      raise ValueError('short_name cannot be longer than 50 ch.')
    if not value.replace('-', '').replace('_', '').isalnum():
      raise ValueError('short_name can only contain a-z, 0-9, -, _')
    
    return value.strip().lower()
  

class LinkUpdate(BaseModel):
  original_url: Optional[HttpUrl] = None
  short_name: Optional[str] = None

  @field_validator('short_name')
  @classmethod
  def validate_short_name(cls, value: str) -> str:
    if value is None:
      return None
    if len(value.strip()) == 0:
      raise ValueError('short_name cannot be empty')
    if len(value) > 50:
      raise ValueError('short_name cannot be longer than 50 ch.')
    if not value.replace('-', '').replace('_', '').isalnum():
      raise ValueError('short_name can only contain a-z, 0-9, -, _')
    
    return value.strip().lower()