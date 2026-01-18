"""
Solana Wallet Activity Tracker API

A production-ready FastAPI application for tracking and retrieving 
Solana wallet activity with comprehensive error handling and validation.

Version: 1.0.0
Author: Solana Wallet API Team
"""

__version__ = "1.0.0"
__title__ = "Solana Wallet Activity API"
__description__ = "Track Solana wallet activity and retrieve transaction history"
__author__ = "Solana Wallet API Team"

from app.main import app

__all__ = ["app", "__version__", "__title__"]
