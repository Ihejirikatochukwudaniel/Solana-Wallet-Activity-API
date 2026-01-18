"""
Configuration settings for the Solana Wallet Activity API.
Loads environment variables using pydantic-settings.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Solana RPC Configuration
    solana_rpc_url: str = "https://api.mainnet-beta.solana.com"
    api_timeout: int = 30
    max_retries: int = 3

    # API Configuration
    api_title: str = "Solana Wallet Activity API"
    api_version: str = "1.0.0"
    api_description: str = "Track Solana wallet activity and retrieve transaction history"

    class Config:
        """Configuration for Settings class."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Constants
LAMPORTS_PER_SOL = 1_000_000_000
MAX_TRANSACTION_LIMIT = 1000
DEFAULT_TRANSACTION_LIMIT = 10

# Initialize settings
settings = Settings()
