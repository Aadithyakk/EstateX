from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    XRPL_RPC_URL: str = Field("https://s.altnet.rippletest.net:51234/", env="XRPL_RPC_URL")
    XRPL_WS_URL: str = Field("wss://s.altnet.rippletest.net:51233/", env="XRPL_WS_URL")
    ISSUER_SEED: str = Field("", env="ISSUER_SEED")
    OPERATOR_SEED: str = Field("", env="OPERATOR_SEED")
    STABLECOIN_ISSUER: str = Field("", env="STABLECOIN_ISSUER")
    DB_URL: str = Field("sqlite:///./dev.db", env="DB_URL")
    ENV: str = Field("dev", env="ENV")
    XRPL_DRY_RUN: bool = Field(True, env="XRPL_DRY_RUN")
    OPENAI_API_KEY: str = Field("", env="OPENAI_API_KEY")

    class Config:
        env_file = ".env"
        # keep environment variable case-insensitive on some platforms
        env_file_encoding = "utf-8"


_settings = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
