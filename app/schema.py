from typing import List
from pydantic import BaseModel

class PaperSchema(BaseModel):
    article_info: List[str]
    citation: int
    year: int
    
class PapersSchema(BaseModel):
    name : str
    papers : List[PaperSchema]

class ScholarInfoSchema(BaseModel):
    name : str
    university: str
    all_citations: int
    h_index: int
    i_10_index: int
    

