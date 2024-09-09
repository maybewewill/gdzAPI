from pydantic import BaseModel

class Solution(BaseModel):
    id: int
    title: str
    image_src: str