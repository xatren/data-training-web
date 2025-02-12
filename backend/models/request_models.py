from pydantic import BaseModel

class CSVAnalysisRequest(BaseModel):
    file_url: str
    file_name: str 