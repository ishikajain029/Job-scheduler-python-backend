from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Job(BaseModel):
    job_name: str
    schedule_time: Optional[str] =None  
    job_details: str

class JobResponse(BaseModel):
    id: str
    job_name: str
    schedule_time: Optional[str] =None  
    last_run: Optional[datetime] = None  
    next_run: Optional[datetime] = None  
    job_details: str
    status:str