from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Business, Product, EconomyAccount


# Employee limit mapping by product level
EMPLOYEE_LIMITS: Dict[str, int] = {
    str(i): 2 if i <= 2 else (3 if i <= 7 else (4 if i <= 12 else (5 if i <= 18 else (6 if i <= 24 else (7 if i <= 39 else 8)))))
    for i in range(1, 41)
}


async def get_business_by_owner(session: AsyncSession, owner_id: int) -> Optional[Business]:
    stmt = (
        select(Business)
        .where(Business.owner_id == owner_id)
        .options(selectinload(Business.products))
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_business_by_name(session: AsyncSession, name: str) -> Optional[Business]:
    stmt = select(Business).where(Business.name.ilike(name))
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def register_business(
    session: AsyncSession, owner_id: int, name: str
) -> Tuple[bool, str, Optional[Business]]:
    name = name.strip()
    if len(name) < 3:
        return False, "Business name must be at least 3 characters long.", None
    if len(name) > 20:
        return False, "Business name must be at most 20 characters long.", None

    existing_owned = await get_business_by_owner(session, owner_id)
    if existing_owned is not None:
        return False, f"You already own a registered business: **{existing_owned.name}**.", None

    existing_name = await get_business_by_name(session, name)
    if existing_name is not None:
        return False, f"A business named **{name}** already exists. Choose a unique name.", None

    business = Business(owner_id=owner_id, name=name, balance=0, company_value=0)
    session.add(business)
    await session.commit()
    return True, "Business registered successfully!", business


async def get_product(
    session: AsyncSession, business_id: int, product_name: str
) -> Optional[Product]:
    stmt = select(Product).where(
        Product.business_id == business_id, Product.name.ilike(product_name.strip())
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_product(
    session: AsyncSession, business_id: int, product_name: str, price: int = 500
) -> Tuple[bool, str, Optional[Product]]:
    product_name = product_name.strip()
    if len(product_name) < 3 or len(product_name) > 20:
        return False, "Product name must be between 3 and 20 characters.", None

    existing = await get_product(session, business_id, product_name)
    if existing is not None:
        return False, f"A product named **{product_name}** already exists in your company.", None

    now = datetime.now(timezone.utc)
    product = Product(
        business_id=business_id,
        name=product_name,
        price=price,
        level=1,
        num_manufactured=0,
        num_employees=0,
        time_to_make_one_product=60,
        last_sold_timestamp=now,
        total_sold=0,
    )
    session.add(product)
    await session.commit()
    return True, "Product created successfully!", product


async def hire_employees(
    session: AsyncSession,
    owner_id: int,
    product_name: str,
    num_employees: int = 1,
    cost_per_employee: int = 100,
) -> Tuple[bool, str]:
    if num_employees <= 0:
        return False, "Number of employees must be positive."

    business = await get_business_by_owner(session, owner_id)
    if business is None:
        return False, "You do not have a registered business."

    product = await get_product(session, business.id, product_name)
    if product is None:
        return False, f"Product '{product_name}' was not found in your business."

    max_allowed = EMPLOYEE_LIMITS.get(str(product.level), 8)
    if product.num_employees + num_employees > max_allowed:
        return (
            False,
            f"You cannot hire that many. Product level {product.level} allows at most {max_allowed} employees (currently: {product.num_employees}).",
        )

    total_cost = num_employees * cost_per_employee
    if business.balance < total_cost:
        return (
            False,
            f"Insufficient business funds. Hiring {num_employees} employees costs {total_cost} iC, but your company balance is {business.balance} iC.",
        )

    business.balance -= total_cost
    product.num_employees += num_employees
    if product.last_sold_timestamp is None:
        product.last_sold_timestamp = datetime.now(timezone.utc)

    await session.commit()
    return True, f"Successfully hired {num_employees} employees for '{product.name}' for {total_cost} iC."


async def fire_employees(
    session: AsyncSession,
    owner_id: int,
    product_name: str,
    num_employees: int = 1,
) -> Tuple[bool, str]:
    if num_employees <= 0:
        return False, "Number of employees must be positive."

    business = await get_business_by_owner(session, owner_id)
    if business is None:
        return False, "You do not have a registered business."

    product = await get_product(session, business.id, product_name)
    if product is None:
        return False, f"Product '{product_name}' was not found in your business."

    if num_employees > product.num_employees:
        return False, f"You only have {product.num_employees} employees assigned to '{product_name}'."

    product.num_employees -= num_employees
    await session.commit()
    return True, f"Successfully discharged {num_employees} employees from '{product.name}'."


async def update_production_status(
    session: AsyncSession, owner_id: int, product_name: str
) -> Tuple[bool, str, Dict]:
    business = await get_business_by_owner(session, owner_id)
    if business is None:
        return False, "You do not have a registered business.", {}

    product = await get_product(session, business.id, product_name)
    if product is None:
        return False, f"Product '{product_name}' was not found.", {}

    now = datetime.now(timezone.utc)
    last_time = product.last_sold_timestamp
    if last_time is None:
        last_time = now
        product.last_sold_timestamp = now

    # Ensure timezone aware
    if last_time.tzinfo is None:
        last_time = last_time.replace(tzinfo=timezone.utc)

    elapsed_seconds = max(0, int((now - last_time).total_seconds()))
    cycle_time = max(10, product.time_to_make_one_product)

    new_produced = (elapsed_seconds // cycle_time) * product.num_employees
    if new_produced > 0:
        product.num_manufactured += new_produced
        # Move forward timestamp by the consumed intervals
        consumed_seconds = (elapsed_seconds // cycle_time) * cycle_time
        product.last_sold_timestamp = last_time + (now - last_time)

    await session.commit()

    return True, "Status updated", {
        "product_name": product.name,
        "price": product.price,
        "level": product.level,
        "employees": product.num_employees,
        "in_stock": product.num_manufactured,
        "total_sold": product.total_sold,
        "elapsed_seconds": elapsed_seconds,
        "business_balance": business.balance,
    }


async def sell_product(
    session: AsyncSession, owner_id: int, product_name: str, quantity: Optional[int] = None
) -> Tuple[bool, str, int]:
    """Sell manufactured product inventory and credit business balance."""
    status_ok, msg, info = await update_production_status(session, owner_id, product_name)
    if not status_ok:
        return False, msg, 0

    business = await get_business_by_owner(session, owner_id)
    product = await get_product(session, business.id, product_name)

    available = product.num_manufactured
    if available <= 0:
        return False, f"No '{product.name}' units in stock to sell. Wait for your employees to manufacture more!", 0

    to_sell = available if quantity is None or quantity <= 0 else min(quantity, available)
    revenue = to_sell * product.price

    product.num_manufactured -= to_sell
    product.total_sold += to_sell
    business.balance += revenue
    business.company_value += revenue // 2

    await session.commit()
    return True, f"Sold {to_sell} units of '{product.name}' for {revenue} iC!", revenue


async def transfer_to_business(
    session: AsyncSession, user_id: int, amount: int
) -> Tuple[bool, str]:
    if amount <= 0:
        return False, "Amount must be greater than zero."

    business = await get_business_by_owner(session, user_id)
    if business is None:
        return False, "You do not have a registered business."

    stmt = select(EconomyAccount).where(EconomyAccount.user_id == user_id)
    result = await session.execute(stmt)
    account = result.scalar_one_or_none()

    if account is None or account.bank < amount:
        return False, "Insufficient bank balance to transfer to business."

    account.bank -= amount
    business.balance += amount
    await session.commit()
    return True, f"Transferred {amount} iC to **{business.name}**."
