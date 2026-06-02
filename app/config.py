from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = ""
    tavily_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"

    model_config = {"env_file": ".env"}


settings = Settings()
