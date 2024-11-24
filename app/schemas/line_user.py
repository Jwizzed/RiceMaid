from pydantic import BaseModel


class LineUserBase(BaseModel):
    user_id: str
    display_name: str
    province: str
