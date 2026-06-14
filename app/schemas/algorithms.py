from pydantic import BaseModel
from typing import List, Optional

class AlgorithmInfo(BaseModel):
    algo_id: str
    name: str
    type: str
    security_level: str
    standard: str
    description: Optional[str] = None
    status: Optional[str] = None
    recommended_use: Optional[str] = None

class AlgorithmsResponse(BaseModel):
    total: int
    algorithms: List[AlgorithmInfo]