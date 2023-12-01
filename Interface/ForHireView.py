import re
import string
import random
import config
import sqlite3
import discord
import datetime

from Interface.BumpView import BumpView
from discord import ButtonStyle, TextStyle
from Interface.JobPostView import ForHirePostView
from Interface.PostApprovalView import PostApprovalView
from discord.ui import View, Button, Modal, TextInput, Select, button

database = sqlite3.connect("./Databases/posts.sqlite")

class PostSubmitView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Submit for review", style=ButtonStyle.blurple, row=1)
    async def submit_for_review_btn(self, interaction: discord.Interaction, button: Button):
        post_id = interaction.message.embeds[0].footer.text[9:]
        await interaction.response.edit_message(
            content="Before submitting, please ensure your post:\n\n- Has good grammar and spelling\n- You have to follow the rules of job marketplace.\n\nYou cannot make changes while your post is pending. If you wish to do so, you'll have to unsubmit your post.\n\nAre you sure you want to submit your post for review?",
            embed=None,
            view=PostFinalView(post_id=post_id)
        )

    @button(label="Edit Post", style=ButtonStyle.gray, row=1)
    async def edit_post_btn(self, interaction: discord.Interaction, button: Button):
        post_id = interaction.message.embeds[0].footer.text[9:]
        post_data = database.execute("SELECT post_title, post_desc, post_payment, post_deadline FROM Posts WHERE post_id = ?", (post_id,)).fetchone()

        post_title = post_data[0]
        post_desc = post_data[1]
        post_payment = post_data[2]

        await interaction.response.send_modal(ForHireEditModal(post_title, post_desc, post_payment))

class NotificationSelectorView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(NotificationSelector())

class NotificationSelector(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Writer", emoji="✍", value=1139895131999322162),
            discord.SelectOption(label="Designer", emoji="🎨", value=1139895133278584883),
            discord.SelectOption(label="Development", emoji="👨‍💻", value=1179955769970532454),
            discord.SelectOption(label="Marketer", emoji="📊", value=1139895135530917960),
            discord.SelectOption(label="Crypto-Web3", emoji="🌐", value=1139895137074413688),
            discord.SelectOption(label="Social Media", emoji="📱", value=1139895138601152662),
            discord.SelectOption(label="Videographer", emoji="📸", value=1139895140119494666),
            discord.SelectOption(label="Staff For-Hire", emoji="👷‍♂️", value=1139895141818183752),
            discord.SelectOption(label="UI/UX Designer", emoji="💻", value=1139895143835648070),
            discord.SelectOption(label="Affiliate Marketing", emoji="👬", value=1139895146004103238),
            discord.SelectOption(label="Video Editors", emoji="🎥", value=1139895434693836830),
            discord.SelectOption(label="Management", emoji="🤵", value=1139895437361430618),
            discord.SelectOption(label="Advertisers", emoji="👨‍💼", value=1139895440540700802),
            discord.SelectOption(label="Assistant", emoji="💁‍♂️", value=1139895443325726721),
            discord.SelectOption(label="Senior Developers", emoji="👨‍💻", value=1139895446714716180),
            discord.SelectOption(label="Part-Time Work", emoji="🕐", value=1139895449453613116),
            discord.SelectOption(label="Tutor", emoji="👨‍🏫", value=1139895600402403348),
            discord.SelectOption(label="Digital Marketing", emoji="💰", value=1139895602461819020),
            discord.SelectOption(label="Others", emoji="❔", value=1139895603850133604),
        ]

        super().__init__(placeholder="Select your post category", options=options, min_values=1, max_values=1)
    
    async def callback(self, interaction: discord.Interaction):
        post_id = interaction.message.embeds[0].footer.text[9:]
        database.execute("UPDATE Posts SET ping_role = ? WHERE post_id = ?", (self.values[0], post_id,)).connection.commit()
        await interaction.response.edit_message(view=PostSubmitView())

class PostFinalView(View):
    def __init__(self, post_id: str):
        self.post_id = post_id
        super().__init__(timeout=None)
    
    @button(label="Submit Post", style=ButtonStyle.blurple)
    async def check_submit_btn(self, interaction: discord.Interaction, button: Button):
        premium_role = interaction.guild.get_role(config.PREMIUM_ROLE_ID)
        vip_role = interaction.guild.get_role(config.VIP_ROLE_ID)
        if premium_role in interaction.user.roles or vip_role in interaction.user.roles:
            post_data = database.execute("SELECT user_id, post_title, post_desc, post_payment, post_deadline, post_type, ping_role FROM Posts WHERE post_id = ?", (self.post_id,)).fetchone()

            post_id = self.post_id
            post_author = interaction.guild.get_member(post_data[0])
            post_title = post_data[1]
            post_description = post_data[2]
            ping_role = interaction.guild.get_role(post_data[6])
            
            post_payment = post_data[3].capitalize()
            for_hire_forum = interaction.guild.get_channel(config.FOR_HIRE_FORUM_ID)
            logging_channel = interaction.guild.get_channel(config.APPROVAL_LOGGING_CHANNEL_ID)

            post_embed = discord.Embed(
                title=f"{config.PERSON_PREMIUM_EMOJI} {post_title}",
                description=f"{config.INVISIBLE_CHARACTER}\n{config.DESCRIPTION_PREMIUM_EMOJI} **Description:**\n{config.TOP_TO_RIGHT_PREMIUM_EMOJI} {post_description}\n{config.INVISIBLE_CHARACTER}",
                color=config.JHM_GOLD
            )
            post_embed.add_field(
                name=f"{config.CARD_PREMIUM_EMOJI} Payment Method:",
                value=f"{config.TOP_TO_RIGHT_PREMIUM_EMOJI} {post_payment}",
                inline=True
            )
            post_embed.add_field(
                name=f"{config.ID_PREMIUM_EMOJI} Client:",
                value=f"{config.TOP_TO_RIGHT_PREMIUM_EMOJI} {post_author.mention}",
                inline=True
            )
            post_embed.set_footer(text="Post ID: {}".format(post_id))
            post_embed.set_image(url=config.PREMIUM_FOR_HIRE_BANNER_URL)

            post_tags = []
            for tag in for_hire_forum.available_tags:
                if tag.name.lower() in ping_role.name.lower():
                        post_tags.append(tag)

            forum_thread = await for_hire_forum.create_thread(name=post_title, content=f"Notification:: {ping_role.mention}", embed=post_embed, applied_tags=post_tags, view=ForHirePostView())
            await forum_thread.thread.send(view=BumpView())

            database.execute("INSERT INTO OutgoingPosts VALUES (?, ?, ?, ?, ?, ?, ?)", (post_id, post_author.id, interaction.user.id, forum_thread.message.id, None, forum_thread.thread.id, round(datetime.datetime.now().timestamp()),)).connection.commit()
            database.execute("UPDATE Posts SET status = ? WHERE post_id = ?", ('auto', post_id,)).connection.commit()
            await interaction.response.edit_message(content="{} Your post have been automatically approved!\nYou can view your post here -> {}".format(config.DONE_EMOJI, forum_thread.message.jump_url), view=None)
            await logging_channel.send(embed=discord.Embed(title="Post Auto Approved", description=f"**Posted By:** {post_author.mention}\n**Post Type:** For Hire Post\n**Approved By:** {interaction.client.user.mention}\n**Post Link:** {forum_thread.thread.jump_url}", color=discord.Color.blue()))
            return
        
        post_data = database.execute("SELECT user_id, post_title, post_desc, post_payment, post_deadline, ping_role FROM Posts WHERE post_id = ?", (self.post_id,)).fetchone()

        post_author = interaction.guild.get_member(post_data[0])
        post_title = post_data[1]
        post_description = post_data[2]
        post_payment = post_data[3]
        post_deadline = "N/A" if not post_data[4] else post_data[4]
        post_ping = interaction.guild.get_role(post_data[5])

        post_approval_channel = interaction.guild.get_channel(config.PAID_JOB_APPROVAL_CHANNEL_ID)

        post_embed = discord.Embed(
            title=f"{config.PERSON_EMOJI} {post_title}",
            description=f"{config.INVISIBLE_CHARACTER}\n{config.DESCRIPTION_EMOJI} **Description:**\n{config.TOP_TO_RIGHT_EMOJI} {post_description}\n{config.INVISIBLE_CHARACTER}",
            color=config.JHM_BLUE
        )
        post_embed.add_field(
            name=f"{config.CARD_EMOJI} Payment Method:",
            value=f"{config.TOP_TO_RIGHT_EMOJI} {post_payment}",
            inline=True
        )
        post_embed.add_field(
            name=f"{config.INFO_EMOJI} Post Information:",
            value=f"- **User:** {post_author.mention} ({post_author.id})\n- **Type:** For Hire Post\n- **Category:** {post_ping.mention}",
            inline=False
        )
        post_embed.set_footer(text="Post ID: {}".format(self.post_id))
        post_embed.set_image(url=config.FOR_HIRE_BANNER_URL)
        
        post_msg = await post_approval_channel.send(embed=post_embed, view=PostApprovalView())
        database.execute("INSERT INTO IncomingPosts VALUES (?, ?, ?)", (self.post_id, post_author.id, post_msg.id,)).connection.commit()
        await interaction.response.edit_message(content="{} Post submitted for approval.".format(config.DONE_EMOJI), embed=None, view=None)

    @button(label="Nevermind", style=ButtonStyle.gray)
    async def nevermind_btn(self, interaction: discord.Interaction, button: Button):
        database.execute("DELETE FROM Posts WHERE post_id = ?", (self.post_id,)).connection.commit()
        await interaction.response.edit_message(content="{} Alright, Have a nice day!".format('👋'), view=None)

class ForHireModal(Modal, title="Creat a For-Hire Post"):
    def __init__(self, _title: str=None, _desc: str=None, _payment: str=None, _deadline: str=None, _portfolio: str=None):
        self._title = _title
        self._desc = _desc
        self._payment = _payment
        self._deadline = _deadline
        self._portfolio = _portfolio

        super().__init__(timeout=None)

        self.post_title = TextInput(
            label="Title",
            placeholder="What service you are offering?",
            style=TextStyle.short,
            default=None if not self._title else self._title,
            required=True,
        )

        self.post_desc = TextInput(
            label="Description",
            placeholder="Please share detail about what you're offering. Tell us about your skills, experience and past work.",
            style=TextStyle.long,
            default=None if not self._desc else self._desc,
            required=True
        )

        self.post_portfolio = TextInput(
            label="Your Portfolio",
            placeholder=" Share Your portfolio link or previous work. if not available , enter N/A",
            style=TextStyle.short,
            default=None if not self._portfolio else self._portfolio,
            required=True
        )
        
        self.post_payment = TextInput(
            label="Payment Method",
            placeholder="What's your preferred payment method?",
            style=TextStyle.short,
            default=None if not self._payment else self._payment,
            required=True
        )

        self.add_item(self.post_title)
        self.add_item(self.post_desc)
        self.add_item(self.post_portfolio)
        self.add_item(self.post_payment)

    async def on_submit(self, interaction: discord.Interaction):
        id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(7)]).upper()

        post_title = self.post_title.value
        post_description = self.post_desc.value
        post_portfolio = self.post_portfolio.value
        post_payment = self.post_payment.value

        post_embed = discord.Embed(
            title=f"{config.PERSON_EMOJI} {post_title}",
            description=f"{config.INVISIBLE_CHARACTER}\n{config.DESCRIPTION_EMOJI} **Description:**\n{config.TOP_TO_RIGHT_EMOJI} {post_description}\n{config.INVISIBLE_CHARACTER}",
            color=config.JHM_BLUE
        )
        post_embed.add_field(
            name=f"{config.INFO_EMOJI} Porfolio:",
            value=f"{config.TOP_TO_RIGHT_EMOJI} {post_portfolio}\n{config.INVISIBLE_CHARACTER}",
            inline=False
        )
        post_embed.add_field(
            name=f"{config.CARD_EMOJI} Payment:",
            value=f"{config.TOP_TO_RIGHT_EMOJI} {post_payment}",
            inline=True
        )
        post_embed.set_footer(text="Post ID: {}".format(id))
        post_embed.set_image(url=config.FOR_HIRE_BANNER_URL)
        
        database.execute(
            '''
                INSERT INTO Posts VALUES (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
            ''',
            (
                id,
                interaction.user.id,
                round(datetime.datetime.now().timestamp()),
                self.post_title.value,
                self.post_desc.value,
                self.post_payment.value,
                None,
                'false',
                'forhire',
                None,
            )
        ).connection.commit()
        
        await interaction.response.send_message(embed=post_embed, view=NotificationSelectorView(), ephemeral=True)

class ForHireEditModal(Modal, title="Creat a For-Hire Post"):
    def __init__(self, _title: str=None, _desc: str=None, _payment: str=None, _deadline: str=None):
        self._title = _title
        self._desc = _desc
        self._payment = _payment
        self._deadline = _deadline

        super().__init__(timeout=None)

        self.post_title = TextInput(
            label="Title",
            placeholder="What service you are offering?",
            style=TextStyle.short,
            default=None if not self._title else self._title,
            required=True,
        )

        self.post_desc = TextInput(
            label="Description",
            placeholder="Please share details about what you're offering.",
            style=TextStyle.long,
            default=None if not self._desc else self._desc,
            required=True
        )

        self.post_payment = TextInput(
            label="Payment Method",
            placeholder="What's your preferred payment method?",
            style=TextStyle.short,
            default=None if not self._payment else self._payment,
            required=True
        )

        self.add_item(self.post_title)
        self.add_item(self.post_desc)
        self.add_item(self.post_payment)

    async def on_submit(self, interaction: discord.Interaction):
        if self.post_deadline.value:
            if not self.post_deadline.value:
                self.post_deadline.value = 'N/A'

        post_id = interaction.message.embeds[0].footer.text[9:]
        data = database.execute("SELECT * FROM Posts WHERE post_id = ?", (post_id,)).fetchone()
        if data:
            post_title = self.post_title.value
            post_description = self.post_desc.value
            post_payment = self.post_payment.value
            post_deadline = "N/A" if not self.post_deadline.value else self.post_deadline.value

            post_embed = discord.Embed(
                title=f"{config.PERSON_EMOJI} {post_title}",
                description=f"{config.INVISIBLE_CHARACTER}\n{config.DESCRIPTION_EMOJI} **Description:**\n{config.TOP_TO_RIGHT_EMOJI} {post_description}\n{config.INVISIBLE_CHARACTER}",
                color=config.JHM_BLUE
            )
            post_embed.add_field(
                name=f"{config.CARD_EMOJI} Budget:",
                value=f"{config.TOP_TO_RIGHT_EMOJI} {post_payment}",
                inline=True
            )
            post_embed.add_field(
                name=f"{config.CLOCK_EMOJI} Deadline:",
                value=f"{config.TOP_TO_RIGHT_EMOJI} {post_deadline}",
                inline=True
            )
            post_embed.set_footer(text="Post ID: {}".format(post_id))
            post_embed.set_image(url=config.FOR_HIRE_BANNER_URL)
            
            database.execute(
                '''
                    UPDATE Posts SET
                        posted_at = ?,
                        post_title = ?,
                        post_desc = ?,
                        post_payment = ?
                    WHERE post_id = ?
                ''',
                (
                    round(datetime.datetime.now().timestamp()),
                    self.post_title.value,
                    self.post_desc.value,
                    self.post_payment.value,
                    post_id,
                )
            ).connection.commit()
        
            await interaction.response.edit_message(embed=post_embed, view=NotificationSelectorView())
        
        else:
            await interaction.response.send_message(content="{} An unexpected error occured! `ERROR: INVALID_DATABASE_ENTRY`".format(config.WARN_EMOJI), ephemeral=True)