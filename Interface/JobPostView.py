import config
import sqlite3
import discord
import datetime

from discord import ButtonStyle, TextStyle
from discord.ui import Modal, View, TextInput, Button, button

database = sqlite3.connect("./Databases/posts.sqlite")

class PostView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Apply", emoji='📝', style=ButtonStyle.blurple, custom_id="apply_button")
    async def apply_button(self, interaction: discord.Interaction, button: Button):
        post_id = interaction.message.embeds[0].footer.text[9:]
        data = database.execute("SELECT user_id FROM OutgoingPosts WHERE post_id = ?", (post_id,)).fetchone()
        post_author = interaction.guild.get_member(int(data[0]))
        await interaction.response.send_message(content=f"The job opportunity has been posted by {post_author.mention} ({post_author.name}). To apply, please reach out directly to their DMs.", ephemeral=True)

    @button(label="Report", emoji='🚨', style=ButtonStyle.red, custom_id="report_btn")
    async def report_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ReportModal())

class PaidJobPostView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @button(label="Apply", emoji='📝', style=ButtonStyle.blurple, custom_id="apply_paid_job_button")
    async def apply_paid_job_btn(self, interaction: discord.Interaction, button: Button):
        post_id = interaction.message.embeds[0].footer.text[9:]
        data = database.execute("SELECT user_id FROM OutgoingPosts WHERE post_id = ?", (post_id,)).fetchone()
        post_author = interaction.guild.get_member(int(data[0]))
        await interaction.response.send_message(content=f"The job opportunity has been posted by {post_author.mention} ({post_author.name}). To apply, please reach out directly to their DMs.", ephemeral=True)

    @button(label="Report", emoji='🚨', style=ButtonStyle.red, custom_id="report_paid_job_button")
    async def report_paid_job_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ReportModal())

class ForHirePostView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @button(label="Connect", emoji='🔗', style=ButtonStyle.blurple, custom_id="connect_forhire_btn")
    async def connect_forhire_btn(self, interaction: discord.Interaction, button: Button):
        post_id = interaction.message.embeds[0].footer.text[9:]
        data = database.execute("SELECT user_id FROM OutgoingPosts WHERE post_id = ?", (post_id,)).fetchone()
        post_author = interaction.guild.get_member(int(data[0]))
        await interaction.response.send_message(content=f"Hey {interaction.user.mention}, to connect with {post_author.display_name}, simply DM ({post_author.mention}) ({post_author.name}) and initiate contact.", ephemeral=True)

    @button(label="Reviews", emoji='⭐', style=ButtonStyle.green, custom_id='reviews_forhire_btn')
    async def reviews_forhire_btn(self, interaction: discord.Interaction, button: Button):
        post_id = interaction.message.embeds[0].footer.text[9:]
        post_data = database.execute("SELECT user_id FROM OutgoingPosts WHERE post_id = ?", (post_id,)).fetchone()
        author = interaction.guild.get_member(int(post_data[0]))
        data = database.execute("SELECT client_id, stars, review FROM Reviews WHERE freelancer_id = ?", (author.id,)).fetchall()

        embed = discord.Embed(
            title=f"{author.display_name}'s Reviews",
            color=discord.Color.blue()
        )

        if data == []:
            embed.description = "No reviews found."
        else:
            for entry in data:
                client = interaction.guild.get_member(entry[0])
                stars = int(entry[1])
                review = str(entry[2])

                embed.add_field(
                    name=f"Review by {client.display_name}",
                    value=f"**Rating:** {'⭐'*stars}\n**Review:** {review.capitalize()}\n{config.INVISIBLE_CHARACTER}",
                    inline=False
                )
            
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @button(label="Report", emoji='🚨', style=ButtonStyle.red, custom_id="report_forhire_btn")
    async def report_forhire_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ReportModal())

class ReportModal(Modal, title="Report Post Modal"):
    def __init__(self):
        super().__init__(timeout=None)
    
    report_description = TextInput(
        label="Description",
        placeholder="Please explain your issue in detail.",
        style=TextStyle.long,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        reports_channel = interaction.guild.get_channel(config.REPORTS_CHANNEL_ID)
        post_id = interaction.message.embeds[0].footer.text[9:]

        data = database.execute("SELECT user_id, posted_at FROM Posts WHERE post_id = ?", (post_id,)).fetchone()
        post_author = interaction.guild.get_member(data[0])

        report_embed = discord.Embed(
            title="Post Reported - {}".format(post_id),
            color=discord.Color.red()
        )
        report_embed.add_field(
            name="Post Information:",
            value=f"**Posted By:** {post_author.mention}\n**Posted On:** <t:{data[1]}:f>\n**Post:** {interaction.message.jump_url}",
            inline=False
        )
        report_embed.add_field(
            name="Report Information:",
            value=f"**Reported By:** {interaction.user.mention}\n**Report Description:** {self.report_description.value}",
            inline=False
        )

        report_msg = await reports_channel.send(embed=report_embed)
        database.execute("INSERT INTO PostReports VALUES (?, ?, ?, ?, ?)", (post_id, report_msg.id, interaction.user.id, round(datetime.datetime.now().timestamp()), 'open')).connection.commit()
        await interaction.response.send_message(content="{} Your report have been submitted.".format(config.REPORT_EMOJI), ephemeral=True)
