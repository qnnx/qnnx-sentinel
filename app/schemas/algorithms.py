from pydantic import BaseModel
from typing import List, Optional

class AlgorithmInfo(BaseModel):
<<<<<<< HEAD
    algo_id: str
=======
    id: str
>>>>>>> saksham-backend
    name: str
    type: str
    security_level: int
    standard: str
    description: Optional[str] = None
<<<<<<< HEAD

class AlgorithmsResponse(BaseModel):
    total: int
    algorithms: List[AlgorithmInfo]
=======
    status: Optional[str] = None
    recommended_use: Optional[str] = None

class AlgorithmsResponse(BaseModel):
    total: int
    algorithms: List[AlgorithmInfo]
>>>>>>> saksham-backend
