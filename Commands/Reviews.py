import config
import sqlite3
import discord

from discord.ext import commands
from discord import app_commands
from Functions.DBController import insert_user_warn

class Reviews(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/posts.sqlite")
    
    reviews_group = app_commands.Group(name="reviews", description="Commands related to reviews system")

    @reviews_group.command(name="give", description="Give review to someone else")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.choices(category=[
        app_commands.Choice(name="Writer", value="Writer"),
        app_commands.Choice(name="Designer", value="Designer"),
        app_commands.Choice(name="Marketer", value="Marketer"),
        app_commands.Choice(name="Crypto-Web3", value="Crypto-Web3"),
        app_commands.Choice(name="Social Media", value="Social Media"),
        app_commands.Choice(name="Videographer", value="Videographer"),
        app_commands.Choice(name="Staff For-Hire", value="Staff For-Hire"),
        app_commands.Choice(name="UI/UX Designer", value="UI/UX Designer"),
        app_commands.Choice(name="Affiliate Marketing", value="Affiliate Marketing"),
        app_commands.Choice(name="Video Editor", value="Video Editor"),
        app_commands.Choice(name="Management", value="Management"),
        app_commands.Choice(name="Advertisers", value="Advertisers"),
        app_commands.Choice(name="Assistant", value="Assistant"),
        app_commands.Choice(name="Senior Developers", value="Senior Developers"),
        app_commands.Choice(name="Part Time Work", value="Part Time Work"),
        app_commands.Choice(name="Tutor", value="Tutor"),
        app_commands.Choice(name="Digital Marketing", value="Digital Marketing"),
        app_commands.Choice(name="Other", value="Other")
    ],
    rating=[
        app_commands.Choice(name="1 Star", value=1),
        app_commands.Choice(name="2 Star", value=2),
        app_commands.Choice(name="3 Star", value=3),
        app_commands.Choice(name="4 Star", value=4),
        app_commands.Choice(name="5 Star", value=5),
    ]
    )
    async def review_give(self, interaction: discord.Interaction, freelancer: discord.Member, client: discord.Member, category: app_commands.Choice[str], rating: app_commands.Choice[int], review: str):
        data = self.database.execute("SELECT * FROM Reviews").fetchall()
        review_number = len(data) + 1

        review_embed = discord.Embed(
            title=f"Review #{review_number:04d}",
            color=discord.Color.blue()
        )
        review_embed.add_field(
            name="Freelancer:",
            value=freelancer.display_name,
            inline=True
        )
        review_embed.add_field(
            name="Client:",
            value=client.display_name,
            inline=True
        )
        review_embed.add_field(
            name="Category:",
            value=category.value,
            inline=True
        )
        review_embed.add_field(
            name="Rating:",
            value="⭐"*rating.value,
            inline=False
        )
        review_embed.add_field(
            name="Review:",
            value=review,
            inline=False
        )
        
        self.database.execute("INSERT INTO Reviews VALUES (?, ?, ?, ?, ?)", (freelancer.id, client.id, category.value, rating.value, review,)).connection.commit()

        await interaction.response.send_message(embed=review_embed)
    
    @app_commands.command(name="warn", description="Warn User")
    async def warn_give(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        insert_user_warn(user.id, reason)
        review_embed = discord.Embed(
            title=f"Warning User",
            color=discord.Color.blue()
        )
        review_embed.add_field(
            name="User:",
            value=user.display_name,
            inline=False
        )
        review_embed.add_field(
            name="Reason:",
            value=reason,
            inline=False
        )
        
        await interaction.response.send_message(embed=review_embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Reviews(bot))