from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_uri : str = Field(..., env = 'DB_URI')
    db_name : str = Field(..., env = 'DB_NAME')
    
    class Config:
        env_file = '.env'
        
@lru_cache
def get_settings():
    return Settings()