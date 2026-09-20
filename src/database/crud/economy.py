from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import EconomyAccount, InventoryItem


async def get_or_create_account(session: AsyncSession, user_id: int) -> EconomyAccount:
    stmt = select(EconomyAccount).where(EconomyAccount.user_id == user_id)
    result = await session.execute(stmt)
    account = result.scalar_one_or_none()
    if account is None:
        account = EconomyAccount(user_id=user_id, wallet=200, bank=0)
        session.add(account)
        await session.flush()
    return account


async def get_balance(session: AsyncSession, user_id: int) -> Dict[str, int]:
    account = await get_or_create_account(session, user_id)
    return {
        "wallet": int(account.wallet),
        "bank": int(account.bank),
        "total": int(account.wallet + account.bank),
    }


async def deposit_money(session: AsyncSession, user_id: int, amount: int) -> bool:
    if amount <= 0:
        return False
    account = await get_or_create_account(session, user_id)
    if account.wallet < amount:
        return False
    account.wallet -= amount
    account.bank += amount
    await session.commit()
    return True


async def withdraw_money(session: AsyncSession, user_id: int, amount: int) -> bool:
    if amount <= 0:
        return False
    account = await get_or_create_account(session, user_id)
    if account.bank < amount:
        return False
    account.bank -= amount
    account.wallet += amount
    await session.commit()
    return True


async def transfer_money(
    session: AsyncSession, from_user_id: int, to_user_id: int, amount: int
) -> bool:
    if amount <= 0 or from_user_id == to_user_id:
        return False

    sender = await get_or_create_account(session, from_user_id)
    if sender.bank < amount:
        return False

    receiver = await get_or_create_account(session, to_user_id)

    sender.bank -= amount
    receiver.bank += amount
    await session.commit()
    return True


async def claim_daily(
    session: AsyncSession, user_id: int, reward: int = 500
) -> Tuple[bool, int, Optional[timedelta]]:
    """
    Claim daily reward.
    Returns: (claimed, reward_amount, time_remaining)
    """
    account = await get_or_create_account(session, user_id)
    now = datetime.now(timezone.utc)

    if account.last_daily is not None:
        # Check if 24 hours have passed
        elapsed = now - account.last_daily
        if elapsed < timedelta(hours=24):
            remaining = timedelta(hours=24) - elapsed
            return False, 0, remaining

    account.wallet += reward
    account.last_daily = now
    await session.commit()
    return True, reward, None


async def get_richest_leaderboard(
    session: AsyncSession, limit: int = 10
) -> List[EconomyAccount]:
    stmt = (
        select(EconomyAccount)
        .order_by(desc(EconomyAccount.wallet + EconomyAccount.bank))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_inventory(
    session: AsyncSession, user_id: int
) -> List[InventoryItem]:
    stmt = (
        select(InventoryItem)
        .where(InventoryItem.user_id == user_id)
        .order_by(InventoryItem.category, InventoryItem.item_name)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def add_item_to_inventory(
    session: AsyncSession,
    user_id: int,
    item_id: str,
    item_name: str,
    category: str = "General",
    amount: int = 1,
) -> InventoryItem:
    stmt = select(InventoryItem).where(
        InventoryItem.user_id == user_id, InventoryItem.item_id == item_id
    )
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()

    if item is None:
        item = InventoryItem(
            user_id=user_id,
            item_id=item_id,
            item_name=item_name,
            category=category,
            quantity=amount,
        )
        session.add(item)
    else:
        item.quantity += amount

    await session.commit()
    return item


async def remove_item_from_inventory(
    session: AsyncSession, user_id: int, item_id: str, amount: int = 1
) -> bool:
    stmt = select(InventoryItem).where(
        InventoryItem.user_id == user_id, InventoryItem.item_id == item_id
    )
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()

    if item is None or item.quantity < amount:
        return False

    item.quantity -= amount
    if item.quantity <= 0:
        await session.delete(item)

    await session.commit()
    return True
