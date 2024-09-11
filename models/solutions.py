from pydantic import BaseModel

class Solution(BaseModel):
    id: int
    title: str | None
    image_src: str