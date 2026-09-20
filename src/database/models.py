from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class UserLevel(Base):
    __tablename__ = "user_levels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, default=0, nullable=False)
    xp: Mapped[int] = mapped_column(BigInteger, default=5, nullable=False)
    level: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "guild_id", name="uq_user_guild_level"),
    )

    def __repr__(self) -> str:
        return f"<UserLevel user_id={self.user_id} guild_id={self.guild_id} xp={self.xp} level={self.level}>"


class EconomyAccount(Base):
    __tablename__ = "economy_accounts"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    wallet: Mapped[int] = mapped_column(BigInteger, default=200, nullable=False)
    bank: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    last_daily: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<EconomyAccount user_id={self.user_id} wallet={self.wallet} bank={self.bank}>"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    item_id: Mapped[str] = mapped_column(String(64), nullable=False)
    item_name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="General", nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "item_id", name="uq_user_item_inventory"),
    )

    def __repr__(self) -> str:
        return f"<InventoryItem user_id={self.user_id} item_id={self.item_id} qty={self.quantity}>"


class GuildSettings(Base):
    __tablename__ = "guild_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    prefix: Mapped[str] = mapped_column(String(10), default="i.", nullable=False)
    welcome_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    welcome_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    welcome_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    leave_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    leave_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    leave_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mod_role_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    mute_role_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    mod_log_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    def __repr__(self) -> str:
        return f"<GuildSettings guild_id={self.guild_id} prefix='{self.prefix}'>"


class CountGame(Base):
    __tablename__ = "count_games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    current_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    __table_args__ = (
        UniqueConstraint("guild_id", "channel_id", name="uq_guild_channel_count"),
    )

    def __repr__(self) -> str:
        return f"<CountGame guild_id={self.guild_id} channel_id={self.channel_id} count={self.current_count}>"


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    balance: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    company_value: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    products: Mapped[List["Product"]] = relationship("Product", back_populates="business", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Business id={self.id} name='{self.name}' owner_id={self.owner_id} balance={self.balance}>"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    price: Mapped[int] = mapped_column(Integer, default=500, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    num_manufactured: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    num_employees: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    time_to_make_one_product: Mapped[int] = mapped_column(Integer, default=600, nullable=False)
    last_sold_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    total_sold: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    business: Mapped["Business"] = relationship("Business", back_populates="products")

    __table_args__ = (
        UniqueConstraint("business_id", "name", name="uq_business_product_name"),
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} name='{self.name}' business_id={self.business_id} level={self.level}>"
