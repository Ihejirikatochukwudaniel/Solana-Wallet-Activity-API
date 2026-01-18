"""
Wallet API router for handling wallet-related endpoints.
Provides endpoints for wallet summary and transaction history.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import WalletSummary, TransactionList, Transaction
from app.services.solana import SolanaClient, SolanaRPCError
from app.config import DEFAULT_TRANSACTION_LIMIT, MAX_TRANSACTION_LIMIT

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/wallet", tags=["wallet"])

# Initialize Solana client
solana_client = SolanaClient()


@router.get("/{address}/summary", response_model=WalletSummary)
async def get_wallet_summary(address: str) -> WalletSummary:
    """
    Get a summary of wallet activity.

    Retrieves wallet balance, transaction count, and last active timestamp.

    Args:
        address: The Solana wallet address

    Returns:
        WalletSummary containing balance, transaction count, and last active time

    Raises:
        HTTPException: If the address is invalid or RPC calls fail
    """
    # Validate address format
    if not address or len(address) < 32 or len(address) > 44:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Solana address. Address must be 32-44 characters, got {len(address)}",
        )

    try:
        # Fetch balance and transaction count concurrently would be ideal,
        # but we'll do sequential calls for clarity
        logger.info(f"Fetching summary for wallet: {address}")

        # Get balance in lamports
        balance_lamports = await solana_client.get_balance(address)

        # Get transaction signatures to count transactions and find last active time
        signatures = await solana_client.get_signatures(address, limit=1)

        tx_count = await solana_client.get_transaction_count(address)

        # Get last active timestamp from the most recent transaction
        last_active = None
        if signatures and len(signatures) > 0:
            block_time = signatures[0].get("blockTime")
            if block_time:
                last_active = solana_client.timestamp_to_datetime(block_time)

        # Convert lamports to SOL
        balance_sol = solana_client.lamports_to_sol(balance_lamports)

        return WalletSummary(
            address=address,
            balance=round(balance_sol, 9),
            balance_lamports=balance_lamports,
            tx_count=tx_count,
            last_active=last_active,
        )

    except SolanaRPCError as e:
        logger.error(f"Solana RPC error for {address}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Solana RPC error: {str(e)}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching summary for {address}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/{address}/transactions", response_model=TransactionList)
async def get_wallet_transactions(
    address: str,
    limit: Optional[int] = Query(
        DEFAULT_TRANSACTION_LIMIT,
        ge=1,
        le=MAX_TRANSACTION_LIMIT,
        description=f"Number of transactions to retrieve (max {MAX_TRANSACTION_LIMIT})",
    ),
) -> TransactionList:
    """
    Get recent transactions for a wallet.

    Retrieves transaction history including signatures, timestamps, slots, status, and fees.

    Args:
        address: The Solana wallet address
        limit: Number of transactions to retrieve (1-1000, default 10)

    Returns:
        TransactionList containing recent transactions

    Raises:
        HTTPException: If the address is invalid or RPC calls fail
    """
    # Validate address format
    if not address or len(address) < 32 or len(address) > 44:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Solana address. Address must be 32-44 characters, got {len(address)}",
        )

    try:
        logger.info(f"Fetching {limit} transactions for wallet: {address}")

        # Get transaction signatures
        signatures = await solana_client.get_signatures(address, limit=limit)

        if not signatures:
            logger.info(f"No transactions found for wallet: {address}")
            return TransactionList(address=address, transactions=[], count=0)

        # Fetch detailed information for each transaction
        # TODO: Consider batching these requests or implementing rate limiting
        # to avoid hitting RPC rate limits on large transaction lists
        transactions = []
        for sig_data in signatures:
            try:
                signature = sig_data.get("signature")
                if not signature:
                    continue

                tx_details = await solana_client.get_transaction_details(signature)

                if tx_details is None:
                    continue

                # Extract fee information
                meta = tx_details.get("meta", {})
                fee = meta.get("fee", 0) if meta else 0

                # Determine transaction status
                err = meta.get("err") if meta else None
                status = "failed" if err else "success"

                # Extract block time
                block_time = sig_data.get("blockTime")
                block_time_dt = solana_client.timestamp_to_datetime(block_time)

                # Get slot number
                slot = sig_data.get("slot", 0)

                transaction = Transaction(
                    signature=signature,
                    block_time=block_time_dt
                    or solana_client.timestamp_to_datetime(0),
                    slot=slot,
                    status=status,
                    fee=fee,
                )
                transactions.append(transaction)

            except Exception as e:
                logger.error(
                    f"Error processing transaction {sig_data.get('signature')}: {str(e)}"
                )
                # Continue processing other transactions on error
                continue

        return TransactionList(
            address=address,
            transactions=transactions,
            count=len(transactions),
        )

    except SolanaRPCError as e:
        logger.error(f"Solana RPC error for {address}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Solana RPC error: {str(e)}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching transactions for {address}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )
