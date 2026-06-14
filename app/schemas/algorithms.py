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
    algo_type: Optional[str] = None
    family: Optional[str] = None
    public_key_size: Optional[str] = None
    private_key_size: Optional[str] = None
    ciphertext_size: Optional[str] = None

class AlgorithmsResponse(BaseModel):
    total: int
    algorithms: List[AlgorithmInfo]
