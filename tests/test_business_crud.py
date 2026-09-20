import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import crud


@pytest.mark.asyncio
async def test_business_lifecycle(db_session: AsyncSession):
    owner_id = 777666555

    # Register business
    ok, msg, b = await crud.business.register_business(db_session, owner_id, "NovaCorp")
    assert ok is True
    assert b.name == "NovaCorp"
    assert b.balance == 0

    # Prevent duplicate name
    dup_ok, dup_msg, _ = await crud.business.register_business(db_session, 888, "NovaCorp")
    assert dup_ok is False

    # Prevent user registering a second business
    own_dup, _, _ = await crud.business.register_business(db_session, owner_id, "SecondCorp")
    assert own_dup is False

    # Create Product
    p_ok, p_msg, prod = await crud.business.create_product(db_session, b.id, "Quantum Chip", price=800)
    assert p_ok is True
    assert prod.price == 800

    # Inject capital
    # First give user bank balance
    acc = await crud.economy.get_or_create_account(db_session, owner_id)
    acc.bank = 5000
    await db_session.commit()

    cap_ok, _ = await crud.business.transfer_to_business(db_session, owner_id, 2000)
    assert cap_ok is True

    b_fresh = await crud.business.get_business_by_owner(db_session, owner_id)
    assert b_fresh.balance == 2000

    # Hire employees
    hire_ok, hire_msg = await crud.business.hire_employees(db_session, owner_id, "Quantum Chip", 2)
    assert hire_ok is True

    # Check business balance deducted (2 * 100 = 200 iC)
    b_after_hire = await crud.business.get_business_by_owner(db_session, owner_id)
    assert b_after_hire.balance == 1800
