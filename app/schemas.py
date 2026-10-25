
from pydantic import BaseModel , ConfigDict , Field

class AskRequest ( BaseModel ) : 
    question : str = Field(min_length = 3 , max_length = 1000)

class DirectAnswer ( BaseModel ) :
    model_config = ConfigDict(extra="forbid")
    answer : str 
    confidence : float = Field( ge = 0.0 , le = 1.0 )
    assumptions : list[str]

class RagDraft(BaseModel) :
    model_config = ConfigDict(extra="forbid")
    answer : str = Field(min_length = 1)
    chunk_ids : list[int]

class Source(BaseModel) :
    chunk_id : int 
    title : str | None
    source : str

class RagAnswer ( BaseModel ) :
    answer : str 
    sources : list[Source]