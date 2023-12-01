import config
import discord
import sqlite3

from discord.ext import commands
from discord import app_commands
from Interface.GenerateEmbedView import EmbedView

class SetupEmbed(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/posts.sqlite")

    @commands.command()
    async def embed_setup(self, context: commands.Context):
        embed = discord.Embed(
            title="<:white_info:1142840597745520762>⠀Marketplace Information⠀<:white_info:1142840597745520762>",
            description="⠀\n\
Discover a thriving freelance ecosystem at Jobs & Hiring, Market. Connect with clients, access projects, and elevate your freelancing journey with expert insights and a supportive community.\n\
\n\
\n\
<:flecha11:1141389220863299655>⠀<#1129902067390099538>: Employers hire workers, paying for necessary tasks, which helps both. Workers earn money and bosses get work done.\n\
\n\
<:flecha11:1141389220863299655>⠀<#1132688915686490203>: People do tasks without getting paid to learn, grow, or help others, supporting their growth and offering assistance.\n\
\n\
<:flecha11:1141389220863299655>⠀<#1132688823785115799>: Skilled professionals offer their services for hire, showing expertise and talents in a dedicated section.\n\
\n\
<:flecha11:1141389220863299655>⠀<#1132688945147285617>: Workers earn a portion from sales, added to their base pay, reflecting a slice of each sale's earnings.\n\
\n\
⠀\n\
<:bullet:1139565912568111148>⠀For detailed information, check: <#1141822304750411907>",
            color=config.JHM_BLUE
        )
        embed.set_image(url="https://i.ibb.co/kgsRHJn/JHM-Banner.png")
        
        await context.send(embed=embed, view=EmbedView())
    
    @app_commands.command(name="delete-post", description="Delete your previously listed posts. THIS ACTION CAN'T BE UNDONE!")
    @app_commands.describe(post_id="ID of the post that you want to delete.")
    async def delete_post(self, interaction: discord.Interaction, post_id: str):
        data = self.database.execute("SELECT message_id, channel_id, forum_id FROM OutgoingPosts WHERE post_id = ? AND user_id=?", (post_id, interaction.user.id,)).fetchone()
        print(data)
        if data is None:
            for role in interaction.user.roles:
                if role.id in config.STAFF_TEAM_IDS:
                    s_data = self.database.execute("SELECT message_id, channel_id, forum_id FROM OutgoingPosts WHERE post_id = ?", (post_id,)).fetchone()
                    post_type_data = self.database.execute("SELECT post_type FROM Posts WHERE post_id = ?", (post_id,)).fetchone()
                    post_channel = None
                    if post_type_data:
                        if post_type_data[0] == 'forhire':
                            post_channel = interaction.guild.get_channel(config.FOR_HIRE_FORUM_ID)
                        if post_type_data[0] == 'paid':
                            post_channel = interaction.guild.get_channel(config.PAID_JOBS_CHANNEL_ID)

                    if post_channel is not None:
                        message = post_channel.get_partial_message(int(s_data[0]))
                        if message is not None:
                            await message.delete()
                    
                    if s_data[1]:
                        channel = interaction.guild.get_channel(int(s_data[1]))
                        if channel is not None:
                            await channel.delete()
                    
                    if s_data[2]:
                        forum_post = interaction.guild.get_thread(int(s_data[2]))
                        if forum_post is not None:
                            await forum_post.delete()
                    
                    self.database.execute("DELETE FROM Posts WHERE post_id = ?", (post_id,)).connection.commit()
                    self.database.execute("DELETE FROM OutgoingPosts WHERE post_id = ?", (post_id,)).connection.commit()
                    return await interaction.response.send_message(content="{} The job post `{}` has been deleted.".format(config.DONE_EMOJI, post_id), ephemeral=True)
            else:
                return await interaction.response.send_message(content=f"You do not own this job post {interaction.user.mention}!", ephemeral=True)
                
        post_type_data = self.database.execute("SELECT post_type FROM Posts WHERE post_id = ?", (post_id,)).fetchone()
        post_channel = None
        if post_type_data:
            if post_type_data[0] == 'forhire':
                post_channel = interaction.guild.get_channel(config.FOR_HIRE_FORUM_ID)
            if post_type_data[0] == 'paid':
                post_channel = interaction.guild.get_channel(config.PAID_JOBS_CHANNEL_ID)

        if post_channel is not None:
            message = post_channel.get_partial_message(int(data[0]))
            if message is not None:
                await message.delete()
        
        if data[1]:
            channel = interaction.guild.get_channel(int(data[1]))
            if channel is not None:
                await channel.delete()
        
        if data[2]:
            forum_post = interaction.guild.get_thread(int(data[2]))
            if forum_post is not None:
                await forum_post.delete()
        
        self.database.execute("DELETE FROM Posts WHERE post_id = ?", (post_id,)).connection.commit()
        self.database.execute("DELETE FROM OutgoingPosts WHERE post_id = ?", (post_id,)).connection.commit()
        await interaction.response.send_message(content="{} Your job post `{}` has been deleted.".format(config.DONE_EMOJI, post_id), ephemeral=True)
        return
        

    @delete_post.autocomplete('post_id')
    async def delete_post_autocomplete(self, interaction: discord.Interaction, current: str):
        data = self.database.execute("SELECT post_id FROM OutgoingPosts WHERE user_id = ?", (interaction.user.id,)).fetchall()

        return [app_commands.Choice(name=f"Post {entry[0]}", value=entry[0]) for entry in data if current in entry[0]]

    @commands.command(name="get")
    async def geT_tags(self, context: commands.Context):
        forum = context.guild.get_channel(config.FOR_HIRE_FORUM_ID)
        print(forum.available_tags)
    
    @commands.command(name="clear")
    @app_commands.checks.has_permissions(administrator=True)
    async def clear(self, ctx: commands.Context, amount: int):
        await ctx.channel.purge(limit=amount)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetupEmbed(bot))