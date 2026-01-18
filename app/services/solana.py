"""
Solana RPC client for interacting with Solana blockchain.
Provides methods to fetch wallet balance, transaction count, and transaction details.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import httpx

from app.config import settings, LAMPORTS_PER_SOL

logger = logging.getLogger(__name__)


class SolanaRPCError(Exception):
    """Custom exception for Solana RPC errors."""

    pass


class SolanaClient:
    """Async HTTP client for Solana RPC API."""

    def __init__(self, rpc_url: str = settings.solana_rpc_url):
        """
        Initialize the Solana RPC client.

        Args:
            rpc_url: The Solana RPC endpoint URL
        """
        self.rpc_url = rpc_url
        self.timeout = settings.api_timeout
        self.max_retries = settings.max_retries

    async def _call_rpc(
        self,
        method: str,
        params: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a JSON-RPC call to Solana.

        Args:
            method: The RPC method name
            params: Optional parameters for the RPC method

        Returns:
            The result of the RPC call

        Raises:
            SolanaRPCError: If the RPC call fails
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or [],
        }

        retry_count = 0
        while retry_count < self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    logger.info(f"Calling RPC method: {method}")
                    response = await client.post(self.rpc_url, json=payload)
                    response.raise_for_status()

                    data = response.json()

                    # Check for RPC errors
                    if "error" in data:
                        error_msg = data.get("error", {}).get("message", "Unknown error")
                        logger.error(f"RPC error: {error_msg}")
                        raise SolanaRPCError(f"RPC error: {error_msg}")

                    return data.get("result")

            except httpx.TimeoutException:
                retry_count += 1
                logger.warning(
                    f"RPC timeout, retry {retry_count}/{self.max_retries}"
                )
                if retry_count >= self.max_retries:
                    raise SolanaRPCError(
                        f"RPC request timed out after {self.max_retries} retries"
                    )

            except httpx.RequestError as e:
                retry_count += 1
                logger.warning(
                    f"RPC request failed: {str(e)}, retry {retry_count}/{self.max_retries}"
                )
                if retry_count >= self.max_retries:
                    raise SolanaRPCError(f"RPC request failed: {str(e)}")

        raise SolanaRPCError("Max retries exceeded")

    async def get_balance(self, address: str) -> int:
        """
        Get the balance of a wallet in lamports.

        Args:
            address: The Solana wallet address

        Returns:
            Balance in lamports

        Raises:
            SolanaRPCError: If the RPC call fails or address is invalid
        """
        if not address:
            raise SolanaRPCError("Address cannot be empty")

        try:
            result = await self._call_rpc("getBalance", [address])
            if result is None:
                return 0
            # getBalance returns {"context": {...}, "value": <balance>}
            if isinstance(result, dict):
                return int(result.get("value", 0))
            return int(result)
        except SolanaRPCError:
            raise
        except Exception as e:
            logger.error(f"Error fetching balance for {address}: {str(e)}")
            raise SolanaRPCError(f"Failed to fetch balance: {str(e)}")

    async def get_transaction_count(self, address: str) -> int:
        """
        Get the total transaction count for a wallet.

        Args:
            address: The Solana wallet address

        Returns:
            Total transaction count

        Raises:
            SolanaRPCError: If the RPC call fails
        """
        if not address:
            raise SolanaRPCError("Address cannot be empty")

        try:
            # TODO: Consider caching transaction counts as they're immutable history
            # Fetch signatures with a reasonable limit to get transaction count
            signatures = await self._call_rpc(
                "getSignaturesForAddress", [address, {"limit": 1000}]
            )
            return len(signatures) if signatures else 0
        except SolanaRPCError:
            raise
        except Exception as e:
            logger.error(f"Error fetching transaction count for {address}: {str(e)}")
            raise SolanaRPCError(f"Failed to fetch transaction count: {str(e)}")

    async def get_signatures(self, address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent transaction signatures for a wallet.

        Args:
            address: The Solana wallet address
            limit: Maximum number of signatures to return (max 1000)

        Returns:
            List of signature objects with metadata

        Raises:
            SolanaRPCError: If the RPC call fails
        """
        if not address:
            raise SolanaRPCError("Address cannot be empty")

        if limit < 1 or limit > 1000:
            raise SolanaRPCError("Limit must be between 1 and 1000")

        try:
            # TODO: Add caching here to reduce RPC calls for popular addresses
            # Consider Redis or in-memory cache with TTL
            result = await self._call_rpc(
                "getSignaturesForAddress",
                [address, {"limit": limit}],
            )
            return result if result else []
        except SolanaRPCError:
            raise
        except Exception as e:
            logger.error(f"Error fetching signatures for {address}: {str(e)}")
            raise SolanaRPCError(f"Failed to fetch signatures: {str(e)}")

    async def get_transaction_details(self, signature: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a transaction.

        Args:
            signature: The transaction signature

        Returns:
            Transaction details or None if not found

        Raises:
            SolanaRPCError: If the RPC call fails
        """
        if not signature:
            raise SolanaRPCError("Signature cannot be empty")

        try:
            result = await self._call_rpc(
                "getTransaction",
                [signature, {"encoding": "json"}],
            )
            return result
        except SolanaRPCError:
            raise
        except Exception as e:
            logger.error(f"Error fetching transaction {signature}: {str(e)}")
            raise SolanaRPCError(f"Failed to fetch transaction: {str(e)}")

    @staticmethod
    def lamports_to_sol(lamports: int) -> float:
        """
        Convert lamports to SOL.

        Args:
            lamports: Amount in lamports

        Returns:
            Amount in SOL
        """
        return lamports / LAMPORTS_PER_SOL

    @staticmethod
    def timestamp_to_datetime(timestamp: Optional[int]) -> Optional[datetime]:
        """
        Convert Unix timestamp to datetime object.

        Args:
            timestamp: Unix timestamp (seconds since epoch)

        Returns:
            datetime object in UTC or None
        """
        if timestamp is None:
            return None
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
