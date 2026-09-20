import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import crud


@pytest.mark.asyncio
async def test_economy_account_lifecycle(db_session: AsyncSession):
    user_id = 111222333

    # Initial balance check (default: wallet=200, bank=0)
    bal = await crud.economy.get_balance(db_session, user_id)
    assert bal["wallet"] == 200
    assert bal["bank"] == 0
    assert bal["total"] == 200

    # Deposit
    ok = await crud.economy.deposit_money(db_session, user_id, 50)
    assert ok is True
    bal = await crud.economy.get_balance(db_session, user_id)
    assert bal["wallet"] == 150
    assert bal["bank"] == 50

    # Overdraft deposit failure
    fail_dep = await crud.economy.deposit_money(db_session, user_id, 9999)
    assert fail_dep is False

    # Withdraw
    ok_with = await crud.economy.withdraw_money(db_session, user_id, 20)
    assert ok_with is True
    bal = await crud.economy.get_balance(db_session, user_id)
    assert bal["wallet"] == 170
    assert bal["bank"] == 30

    # Transfer
    recipient_id = 444555666
    ok_xfer = await crud.economy.transfer_money(db_session, user_id, recipient_id, 25)
    assert ok_xfer is True

    sender_bal = await crud.economy.get_balance(db_session, user_id)
    recip_bal = await crud.economy.get_balance(db_session, recipient_id)
    assert sender_bal["bank"] == 5
    assert recip_bal["bank"] == 25


@pytest.mark.asyncio
async def test_inventory_crud(db_session: AsyncSession):
    user_id = 999888777

    # Add item
    item = await crud.economy.add_item_to_inventory(
        db_session, user_id, "smart-watch", "Smart Watch", "IoT", 2
    )
    assert item.quantity == 2

    # Query inventory
    inv = await crud.economy.get_inventory(db_session, user_id)
    assert len(inv) == 1
    assert inv[0].item_id == "smart-watch"
    assert inv[0].quantity == 2

    # Remove partial quantity
    rem_ok = await crud.economy.remove_item_from_inventory(db_session, user_id, "smart-watch", 1)
    assert rem_ok is True
    inv = await crud.economy.get_inventory(db_session, user_id)
    assert inv[0].quantity == 1

    # Remove remaining
    rem_all = await crud.economy.remove_item_from_inventory(db_session, user_id, "smart-watch", 1)
    assert rem_all is True
    inv = await crud.economy.get_inventory(db_session, user_id)
    assert len(inv) == 0
