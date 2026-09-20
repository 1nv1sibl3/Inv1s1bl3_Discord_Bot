from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

from src.bot.utils.embeds import branded_embed, success_embed, error_embed, info_embed
from src.bot.utils.formatting import format_currency, format_timespan
from src.database.session import get_db_session
from src.database import crud


class BusinessCog(commands.Cog, name="Business"):
    """Venture capital and virtual enterprise simulation."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="bregister", brief="Register and incorporate your business company.")
    @app_commands.describe(business_name="The name of your company (3-20 characters)")
    async def register_company(self, ctx: commands.Context, *, business_name: str):
        async with get_db_session() as session:
            ok, msg, business = await crud.business.register_business(session, ctx.author.id, business_name)

        if not ok:
            await ctx.send(embed=error_embed("Registration Failed", msg))
        else:
            embed = success_embed(
                "Company Incorporated!",
                f"Congratulations! **{business.name}** is now officially open for business.\n"
                f"Use `{ctx.prefix}bproduct <name>` to launch your first product line.",
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="bproduct", brief="Create a new product line for your company.")
    @app_commands.describe(product_name="Name of your product", price="Selling price per unit (default: 500)")
    async def add_product(self, ctx: commands.Context, product_name: str, price: int = 500):
        if price <= 0:
            await ctx.send(embed=error_embed("Invalid Price", "Selling price must be greater than zero."))
            return

        async with get_db_session() as session:
            business = await crud.business.get_business_by_owner(session, ctx.author.id)
            if business is None:
                await ctx.send(embed=error_embed("No Business Found", f"You must register a business first using `{ctx.prefix}bregister <name>`."))
                return

            ok, msg, prod = await crud.business.create_product(session, business.id, product_name, price)

        if not ok:
            await ctx.send(embed=error_embed("Product Creation Failed", msg))
        else:
            embed = success_embed(
                "Product Created",
                f"Created product **{prod.name}** with price **{format_currency(prod.price)}**!\n"
                f"Hire workforce using `{ctx.prefix}hire \"{prod.name}\" <count>` to begin production.",
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="hire", brief="Hire employees to manufacture your product.")
    @app_commands.describe(product_name="Product to assign workers to", num_employees="Number of workers to hire")
    async def hire_workers(self, ctx: commands.Context, product_name: str, num_employees: int = 1):
        async with get_db_session() as session:
            ok, msg = await crud.business.hire_employees(session, ctx.author.id, product_name, num_employees)

        if not ok:
            await ctx.send(embed=error_embed("Hiring Failed", msg))
        else:
            await ctx.send(embed=success_embed("Workforce Expanded", msg))

    @commands.hybrid_command(name="fire", brief="Discharge employees from manufacturing a product.")
    @app_commands.describe(product_name="Product to remove workers from", num_employees="Number of workers to fire")
    async def fire_workers(self, ctx: commands.Context, product_name: str, num_employees: int = 1):
        async with get_db_session() as session:
            ok, msg = await crud.business.fire_employees(session, ctx.author.id, product_name, num_employees)

        if not ok:
            await ctx.send(embed=error_embed("Action Failed", msg))
        else:
            await ctx.send(embed=success_embed("Staff Discharged", msg))

    @commands.hybrid_command(name="bstatus", aliases=["bs"], brief="Inspect manufacturing metrics and stock for a product.")
    @app_commands.describe(product_name="Product name to inspect")
    async def production_status(self, ctx: commands.Context, product_name: str):
        async with get_db_session() as session:
            ok, msg, data = await crud.business.update_production_status(session, ctx.author.id, product_name)

        if not ok:
            await ctx.send(embed=error_embed("Status Check Failed", msg))
            return

        embed = branded_embed(
            title=f"🏭 Production Status: {data['product_name']}",
            description="Real-time manufacturing analytics and inventory.",
        )
        embed.add_field(name="Assigned Workers", value=f"`{data['employees']}`", inline=True)
        embed.add_field(name="Current Stock", value=f"`{data['in_stock']:,} units`", inline=True)
        embed.add_field(name="Retail Price", value=f"`{format_currency(data['price'])}`", inline=True)

        embed.add_field(name="Total Units Sold", value=f"`{data['total_sold']:,}`", inline=True)
        embed.add_field(name="Company Treasury", value=f"`{format_currency(data['business_balance'])}`", inline=True)
        embed.add_field(name="Elapsed Cycle Time", value=f"`{format_timespan(data['elapsed_seconds'])}`", inline=True)

        embed.set_footer(text=f"Sell manufactured inventory with {ctx.prefix}bsell \"{data['product_name']}\"")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="bsell", brief="Sell manufactured products in stock for company revenue.")
    @app_commands.describe(product_name="Product to sell", quantity="Optional quantity (defaults to all stock)")
    async def sell_stock(self, ctx: commands.Context, product_name: str, quantity: Optional[int] = None):
        async with get_db_session() as session:
            ok, msg, revenue = await crud.business.sell_product(session, ctx.author.id, product_name, quantity)

        if not ok:
            await ctx.send(embed=error_embed("Sale Incomplete", msg))
        else:
            await ctx.send(embed=success_embed("Inventory Sold!", f"{msg}\nRevenue has been credited to your business balance."))

    @commands.hybrid_command(name="bpay", brief="Inject capital into your business from your personal bank.")
    @app_commands.describe(amount="Amount of iCoin to transfer into business")
    async def transfer_capital(self, ctx: commands.Context, amount: int):
        async with get_db_session() as session:
            ok, msg = await crud.business.transfer_to_business(session, ctx.author.id, amount)

        if not ok:
            await ctx.send(embed=error_embed("Transfer Failed", msg))
        else:
            await ctx.send(embed=success_embed("Capital Injected", msg))

    @commands.hybrid_command(name="binfo", brief="View detailed company overview and product portfolio.")
    async def company_info(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        target = member or ctx.author
        async with get_db_session() as session:
            business = await crud.business.get_business_by_owner(session, target.id)

        if business is None:
            msg = "You do not own a business yet." if target == ctx.author else f"{target.display_name} does not own a business."
            await ctx.send(embed=info_embed("No Enterprise Found", msg))
            return

        embed = branded_embed(
            title=f"🏢 Enterprise Profile: {business.name}",
            description=f"Proprietor: {target.mention}\nEstablished: <t:{int(business.created_at.timestamp())}:R>",
        )
        embed.add_field(name="Company Treasury", value=f"`{format_currency(business.balance)}`", inline=True)
        embed.add_field(name="Valuation", value=f"`{format_currency(business.company_value)}`", inline=True)
        embed.add_field(name="Active Products", value=f"`{len(business.products)}`", inline=True)

        if business.products:
            lines = [
                f"• **{p.name}** | Price: {format_currency(p.price)} | Workers: {p.num_employees} | Stock: {p.num_manufactured}"
                for p in business.products[:10]
            ]
            embed.add_field(name="Product Portfolio", value="\n".join(lines), inline=False)

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BusinessCog(bot))
