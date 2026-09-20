import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

import discord
from discord import app_commands
from discord.ext import commands

from src.bot.utils.embeds import branded_embed, success_embed, error_embed, info_embed
from src.bot.utils.formatting import create_progress_bar, format_currency, format_timespan
from src.database.session import get_db_session
from src.database import crud

logger = logging.getLogger("inv1s1bl3.cogs.economy")

# Load market dataset from assets/data/market.json
_MARKET_FILE = Path(__file__).resolve().parent.parent.parent.parent / "assets" / "data" / "market.json"
MARKET_DATA: Dict[str, List] = {}
MARKET_ITEMS: Dict[str, Dict] = {}

if _MARKET_FILE.exists():
    try:
        with open(_MARKET_FILE, "r", encoding="utf-8") as f:
            MARKET_DATA = json.load(f)
            for category, items in MARKET_DATA.items():
                for item in items:
                    # item format: [Display Name, Price, Item ID]
                    if len(item) >= 3:
                        MARKET_ITEMS[item[2].lower()] = {
                            "name": item[0],
                            "price": item[1],
                            "id": item[2].lower(),
                            "category": category,
                        }
    except Exception as e:
        logger.error(f"Failed to load market.json: {e}")


class Economy(commands.Cog, name="Economy & Levels"):
    """Leveling, virtual banking, market trading, and inventory management."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Award XP on non-bot messages."""
        if message.author.bot or not message.guild:
            return

        try:
            async with get_db_session() as session:
                _, leveled_up, new_level = await crud.users.increase_xp(
                    session, message.author.id, message.guild.id, rate=10
                )
                if leveled_up and new_level % 5 == 0:
                    # Occasional level celebration
                    await message.channel.send(
                        f"🎉 Congratulations {message.author.mention}, you've reached **Level {new_level}**!"
                    )
        except Exception as e:
            logger.debug(f"Error increasing XP: {e}")

    @commands.hybrid_command(name="rank", brief="View your or another member's server level and XP card.")
    @commands.guild_only()
    @app_commands.describe(member="Member to view rank for")
    async def rank(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        target = member or ctx.author
        async with get_db_session() as session:
            data = await crud.users.get_user_data(session, target.id, ctx.guild.id)
            server_rank = await crud.users.get_rank(session, target.id, ctx.guild.id)

        xp = data["xp"]
        level = data["level"]
        next_level_xp = int((level + 1) ** 4)
        current_level_base_xp = int(level ** 4)

        needed = max(1, next_level_xp - current_level_base_xp)
        progress = max(0, xp - current_level_base_xp)
        bar = create_progress_bar(progress, needed, length=12)

        embed = branded_embed(
            title=f"📊 {target.display_name}'s Level Stats",
            description=f"Server Ranking: **#{server_rank}**",
        )
        embed.add_field(name="Current Level", value=f"`Level {level}`", inline=True)
        embed.add_field(name="Total Experience", value=f"`{xp:,} XP`", inline=True)
        embed.add_field(name="Progress to Next Level", value=f"{bar}\n`{progress:,} / {needed:,} XP`", inline=False)
        embed.set_thumbnail(url=target.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="grank", brief="View global cross-server ranking.")
    @app_commands.describe(member="Member to view global rank for")
    async def global_rank(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        target = member or ctx.author
        async with get_db_session() as session:
            global_rank = await crud.users.get_global_ranking(session, target.id)

        embed = branded_embed(
            title=f"🌐 Global Ranking: {target.display_name}",
            description=f"Worldwide Network Rank: **#{global_rank}**",
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="leaderboard", aliases=["lb", "top"], brief="Display the server experience leaderboard.")
    @commands.guild_only()
    async def server_leaderboard(self, ctx: commands.Context):
        async with get_db_session() as session:
            top_users = await crud.users.get_server_leaderboard(session, ctx.guild.id, limit=10)

        if not top_users:
            await ctx.send(embed=info_embed("Leaderboard Empty", "No activity recorded in this server yet!"))
            return

        lines = []
        for rank_num, entry in enumerate(top_users, 1):
            member = ctx.guild.get_member(entry.user_id)
            name = member.display_name if member else f"User {entry.user_id}"
            lines.append(f"`#{rank_num:02d}` **{name}** — Level {entry.level} (`{entry.xp:,} XP`)")

        embed = branded_embed(
            title=f"🏆 Server Leaderboard: {ctx.guild.name}",
            description="\n".join(lines),
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="balance", aliases=["bal", "money"], brief="Check your wallet and bank balance.")
    @app_commands.describe(member="Member to view balance for")
    async def balance(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        target = member or ctx.author
        async with get_db_session() as session:
            bal = await crud.economy.get_balance(session, target.id)

        embed = branded_embed(
            title=f"💰 Account Balance: {target.display_name}",
            description="Official Inv1s1bl3 Coin (iC) Banking Summary",
        )
        embed.add_field(name="💵 Wallet", value=f"`{format_currency(bal['wallet'])}`", inline=True)
        embed.add_field(name="🏦 Bank", value=f"`{format_currency(bal['bank'])}`", inline=True)
        embed.add_field(name="🪙 Net Worth", value=f"`{format_currency(bal['total'])}`", inline=True)
        embed.set_thumbnail(url=target.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="deposit", aliases=["dep"], brief="Deposit iCoin from your wallet to your bank.")
    @app_commands.describe(amount="Amount of coins to deposit")
    async def deposit(self, ctx: commands.Context, amount: int):
        if amount <= 0:
            await ctx.send(embed=error_embed("Invalid Amount", "Deposit amount must be greater than zero."))
            return

        async with get_db_session() as session:
            ok = await crud.economy.deposit_money(session, ctx.author.id, amount)

        if not ok:
            await ctx.send(embed=error_embed("Insufficient Wallet Funds", "You do not have enough coins in your wallet."))
        else:
            await ctx.send(embed=success_embed("Deposit Successful", f"Deposited **{format_currency(amount)}** into your bank account."))

    @commands.hybrid_command(name="withdraw", aliases=["with"], brief="Withdraw iCoin from your bank to your wallet.")
    @app_commands.describe(amount="Amount of coins to withdraw")
    async def withdraw(self, ctx: commands.Context, amount: int):
        if amount <= 0:
            await ctx.send(embed=error_embed("Invalid Amount", "Withdrawal amount must be greater than zero."))
            return

        async with get_db_session() as session:
            ok = await crud.economy.withdraw_money(session, ctx.author.id, amount)

        if not ok:
            await ctx.send(embed=error_embed("Insufficient Bank Funds", "You do not have enough coins in your bank."))
        else:
            await ctx.send(embed=success_embed("Withdrawal Complete", f"Withdrew **{format_currency(amount)}** to your wallet."))

    @commands.hybrid_command(name="transfer", aliases=["pay", "give", "send"], brief="Transfer bank coins to another member.")
    @app_commands.describe(member="Recipient member", amount="Amount to send from bank")
    async def transfer(self, ctx: commands.Context, member: discord.Member, amount: int):
        if member.id == ctx.author.id:
            await ctx.send(embed=error_embed("Invalid Transfer", "You cannot transfer funds to yourself."))
            return

        if member.bot:
            await ctx.send(embed=error_embed("Invalid Transfer", "You cannot transfer coins to a bot."))
            return

        if amount <= 0:
            await ctx.send(embed=error_embed("Invalid Amount", "Transfer amount must be greater than zero."))
            return

        async with get_db_session() as session:
            ok = await crud.economy.transfer_money(session, ctx.author.id, member.id, amount)

        if not ok:
            await ctx.send(embed=error_embed("Transfer Failed", "Insufficient bank funds to complete this wire transfer."))
        else:
            await ctx.send(
                embed=success_embed(
                    "Transfer Complete",
                    f"Successfully transferred **{format_currency(amount)}** to {member.mention}.",
                )
            )

    @commands.hybrid_command(name="daily", aliases=["d"], brief="Claim your 24-hour daily stipend.")
    async def daily_reward(self, ctx: commands.Context):
        async with get_db_session() as session:
            claimed, reward, remaining = await crud.economy.claim_daily(session, ctx.author.id, reward=500)

        if not claimed and remaining is not None:
            time_str = format_timespan(int(remaining.total_seconds()))
            await ctx.send(embed=warning_embed("Stipend Claimed", f"You have already claimed your daily reward! Return in **{time_str}**."))
        else:
            await ctx.send(embed=success_embed("Daily Stipend", f"You received your daily reward of **{format_currency(reward)}**!"))

    @commands.hybrid_command(name="moneyboard", aliases=["rich"], brief="Display the wealthiest bot citizens.")
    async def richest_users(self, ctx: commands.Context):
        async with get_db_session() as session:
            richest = await crud.economy.get_richest_leaderboard(session, limit=10)

        if not richest:
            await ctx.send(embed=info_embed("Banking Registry", "No registered accounts found."))
            return

        lines = []
        for rank_num, acc in enumerate(richest, 1):
            user = self.bot.get_user(acc.user_id)
            name = user.name if user else f"User {acc.user_id}"
            lines.append(f"`#{rank_num:02d}` **{name}** — {format_currency(acc.wallet + acc.bank)}")

        embed = branded_embed(
            title="💎 Richest Members Worldwide",
            description="\n".join(lines),
        )
        await ctx.send(embed=embed)

    @commands.hybrid_group(name="imkt", aliases=["market"], brief="Browse items available in the Inv1s1bl3 Market.")
    async def market_group(self, ctx: commands.Context):
        """Browse market departments."""
        categories = list(MARKET_DATA.keys())
        embed = branded_embed(
            title="🏬 Inv1s1bl3 Grand Market",
            description=(
                "Welcome to the general store! Browse catalogs by category:\n"
                + "\n".join(f"• `{ctx.prefix}imkt {c.lower()}` — {c}" for c in categories)
                + f"\n\nBuy an item with `{ctx.prefix}buy <item_id> [qty]`"
            ),
        )
        await ctx.send(embed=embed)

    @market_group.command(name="iot", brief="Browse IoT and Smart Electronics.")
    async def market_iot(self, ctx: commands.Context):
        await self._show_category_items(ctx, "IoT")

    @market_group.command(name="veg", aliases=["food"], brief="Browse food and beverage items.")
    async def market_food(self, ctx: commands.Context):
        await self._show_category_items(ctx, "Veg")

    @market_group.command(name="vehicles", aliases=["cars"], brief="Browse vehicles and transportation.")
    async def market_vehicles(self, ctx: commands.Context):
        await self._show_category_items(ctx, "Vehicles")

    @market_group.command(name="clothes", brief="Browse apparel and fashion.")
    async def market_clothes(self, ctx: commands.Context):
        await self._show_category_items(ctx, "Clothes")

    async def _show_category_items(self, ctx: commands.Context, category_name: str):
        items = MARKET_DATA.get(category_name, [])
        if not items:
            await ctx.send(embed=info_embed(f"Catalog: {category_name}", "No items currently listed."))
            return

        lines = [f"• **{it[0]}** — `{format_currency(it[1])}` (ID: `{it[2]}`)" for it in items[:25]]
        embed = branded_embed(
            title=f"🛍️ Market Catalog: {category_name}",
            description="\n".join(lines),
        )
        embed.set_footer(text=f"To purchase: {ctx.prefix}buy <id> [quantity]")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="buy", aliases=["purchase"], brief="Purchase an item from the market.")
    @app_commands.describe(item_id="Market Item ID (e.g. smart-watch, laptop)", quantity="Quantity to purchase")
    async def buy_item(self, ctx: commands.Context, item_id: str, quantity: int = 1):
        if quantity <= 0:
            await ctx.send(embed=error_embed("Invalid Quantity", "Quantity must be at least 1."))
            return

        item_key = item_id.lower().strip()
        item = MARKET_ITEMS.get(item_key)
        if not item:
            await ctx.send(embed=error_embed("Item Not Found", f"No item with ID `{item_id}` exists in the market."))
            return

        total_cost = item["price"] * quantity
        async with get_db_session() as session:
            bal = await crud.economy.get_balance(session, ctx.author.id)
            if bal["wallet"] < total_cost:
                await ctx.send(
                    embed=error_embed(
                        "Insufficient Funds",
                        f"You need **{format_currency(total_cost)}** in your wallet to buy {quantity}x {item['name']}, but you only have **{format_currency(bal['wallet'])}**.",
                    )
                )
                return

            # Deduct wallet & add to inventory
            account = await crud.economy.get_or_create_account(session, ctx.author.id)
            account.wallet -= total_cost
            await crud.economy.add_item_to_inventory(
                session, ctx.author.id, item["id"], item["name"], item["category"], quantity
            )

        await ctx.send(
            embed=success_embed(
                "Purchase Successful",
                f"Purchased **{quantity}x {item['name']}** for **{format_currency(total_cost)}**!\nCheck your inventory with `{ctx.prefix}inventory`.",
            )
        )

    @commands.hybrid_command(name="inventory", aliases=["inv", "bag"], brief="View the items in your bag.")
    async def inventory(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        target = member or ctx.author
        async with get_db_session() as session:
            items = await crud.economy.get_inventory(session, target.id)

        if not items:
            msg = "Your inventory is currently empty!" if target == ctx.author else f"{target.display_name}'s inventory is empty."
            await ctx.send(embed=info_embed("🎒 Backpack Inventory", msg))
            return

        lines = [f"• **{it.item_name}** ×`{it.quantity}` (Category: `{it.category}` | ID: `{it.item_id}`)" for it in items]
        embed = branded_embed(
            title=f"🎒 {target.display_name}'s Inventory",
            description="\n".join(lines),
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="sell", brief="Sell an item from your inventory back to the market for a 50% refund.")
    @app_commands.describe(item_id="Item ID to sell", quantity="Quantity to sell")
    async def sell_item(self, ctx: commands.Context, item_id: str, quantity: int = 1):
        if quantity <= 0:
            await ctx.send(embed=error_embed("Invalid Quantity", "Quantity must be at least 1."))
            return

        item_key = item_id.lower().strip()
        item_meta = MARKET_ITEMS.get(item_key)
        base_price = item_meta["price"] if item_meta else 100
        refund_per_unit = max(1, base_price // 2)
        total_refund = refund_per_unit * quantity

        async with get_db_session() as session:
            removed = await crud.economy.remove_item_from_inventory(
                session, ctx.author.id, item_key, quantity
            )
            if not removed:
                await ctx.send(embed=error_embed("Sale Failed", f"You do not have {quantity}x `{item_id}` in your inventory."))
                return

            account = await crud.economy.get_or_create_account(session, ctx.author.id)
            account.wallet += total_refund
            await session.commit()

        item_name = item_meta["name"] if item_meta else item_id
        await ctx.send(
            embed=success_embed(
                "Item Sold",
                f"Sold **{quantity}x {item_name}** for **{format_currency(total_refund)}** (credited to wallet).",
            )
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Economy(bot))
