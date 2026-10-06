import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()
@dataclass(frozen=True)
class Settings:
    openai_api_key: str=os.getenv("OPENAI_API_KEY","")
    tradier_token: str=os.getenv("TRADIER_TOKEN","")
    openai_model: str=os.getenv("OPENAI_MODEL","gpt-5.6")
    tradier_base_url: str=os.getenv("TRADIER_BASE_URL","https://api.tradier.com/v1")
    db_path: str=os.getenv("PAPER_TIGER_DB","paper_tiger.db")
    def validate(self):
        missing=[k for k,v in {"OPENAI_API_KEY":self.openai_api_key,"TRADIER_TOKEN":self.tradier_token}.items() if not v]
        if missing: raise RuntimeError("Missing environment variables: "+", ".join(missing))
