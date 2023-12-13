import re
import string
import random
import config
import sqlite3
import discord
import datetime

from discord import ButtonStyle, TextStyle
from Interface.JobPostView import PaidJobPostView
from Interface.PostApprovalView import PostApprovalView
from discord.ui import View, Button, Modal, TextInput, Select, button
from Functions.DBController import (
    insert_paid_job_post,
    update_for_fire_post_ping_role,
    find_post_by_post_id,
    update_paid_job_post,
    update_for_fire_post_status,
    insert_out_going_post,
    insert_incoming_post,
    post_remove
)

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
        post_data = find_post_by_post_id(post_id)

        post_title = post_data.post_title
        post_desc = post_data.post_desc
        post_payment = post_data.post_payment
        post_deadline = None if post_data.post_deadline == 'N/A' else post_data.post_deadline

        await interaction.response.send_modal(PostEditModal(post_title, post_desc, post_payment, post_deadline))

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
        update_for_fire_post_ping_role(post_id, self.values[0])
        await interaction.response.edit_message(view=PostSubmitView())

class PostFinalView(View):
    def __init__(self, post_id: str):
        self.post_id = post_id
        super().__init__(timeout=None)
    
    @button(label="Submit Post", style=ButtonStyle.blurple)
    async def check_submit_btn(self, interaction: discord.Interaction, button: Button):
        premium_role = interaction.guild.get_role(config.PREMIUM_ROLE_ID)
        vip_role = interaction.guild.get_role(config.VIP_ROLE_ID)
        post_data = find_post_by_post_id(self.post_id)
        post_id = self.post_id
        post_author = interaction.guild.get_member(post_data.user_id)
        post_title = post_data.post_title
        post_description = post_data.post_desc
        post_deadline = "N/A" if not post_data.post_deadline else post_data.post_deadline
        ping_role = interaction.guild.get_role(post_data.ping_role)
        post_payment = post_data.post_payment
        
        if premium_role in interaction.user.roles or vip_role in interaction.user.roles:
            paid_jobs_channel = interaction.guild.get_channel(config.PAID_JOBS_CHANNEL_ID)
            logging_channel = interaction.guild.get_channel(config.APPROVAL_LOGGING_CHANNEL_ID)

            post_embed = discord.Embed(
                title=f"{config.PERSON_PREMIUM_EMOJI} {post_title}",
                description=f"{config.INVISIBLE_CHARACTER}\n{config.DESCRIPTION_PREMIUM_EMOJI} **Description:**\n{config.TOP_TO_RIGHT_PREMIUM_EMOJI} {post_description}\n{config.INVISIBLE_CHARACTER}",
                color=config.JHM_GOLD
            )
            post_embed.add_field(
                name=f"{config.CARD_PREMIUM_EMOJI} Budget:",
                value=f"{config.TOP_TO_RIGHT_PREMIUM_EMOJI} {post_payment}",
                inline=True
            )
            post_embed.add_field(
                name=f"{config.CLOCK_PREMIUM_EMOJI} Deadline:",
                value=f"{config.TOP_TO_RIGHT_PREMIUM_EMOJI} {post_deadline}",
                inline=True
            )
            post_embed.add_field(
                name=f"{config.ID_PREMIUM_EMOJI} Client:",
                value=f"{config.TOP_TO_RIGHT_PREMIUM_EMOJI} {post_author.mention}",
                inline=True
            )
            post_embed.set_footer(text="Post ID: {}".format(post_id))
            post_embed.set_image(url=config.PREMIUM_PAID_JOB_BANNER_URL)

            post_msg = await paid_jobs_channel.send(content=f"Notification: {ping_role.mention}", embed=post_embed, view=PaidJobPostView())
            update_for_fire_post_status(post_id, "auto")
            insert_out_going_post(post_id, post_author.id, interaction.user.id, post_msg.id, "NULL")
            await interaction.response.edit_message(content="{} Your post has been automatically approved because of your premium status!\nYou can view your post here -> {}".format(config.DONE_EMOJI, post_msg.jump_url), view=None)
            await logging_channel.send(embed=discord.Embed(title="Post Auto Approved", description=f"**Posted By:** {post_author.mention}\n**Post Type:** Paid Job\n**Approved By:** {interaction.client.user.mention}\n**Post Link:** {post_msg.jump_url}", color=discord.Color.blue()))
            return

        post_approval_channel = interaction.guild.get_channel(config.PAID_JOB_APPROVAL_CHANNEL_ID)

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
        post_embed.add_field(
            name=f"{config.INFO_EMOJI} Post Information:",
            value=f"- **User:** {post_author.mention} ({post_author.id})\n- **Type:** Paid Job Post\n- **Category:** {ping_role.mention}",
            inline=False
        )
        post_embed.set_footer(text="Post ID: {}".format(self.post_id))
        post_embed.set_image(url=config.PAID_JOB_BANNER_URL)
        
        post_msg = await post_approval_channel.send(embed=post_embed, view=PostApprovalView())
        insert_incoming_post(self.post_id, post_author.id, post_msg.id)
        await interaction.response.edit_message(content="{} Post submitted for approval.".format(config.DONE_EMOJI), embed=None, view=None)

    @button(label="Nevermind", style=ButtonStyle.gray)
    async def nevermind_btn(self, interaction: discord.Interaction, button: Button):
        post_remove(self.post_id)
        await interaction.response.edit_message(content="{} Alright, Have a nice day!".format('👋'), view=None)

class PostModal(Modal, title="Create a Paid Job Post"):
    def __init__(self, _title: str=None, _desc: str=None, _payment: str=None, _deadline: str=None):
        self._title = _title
        self._desc = _desc
        self._payment = _payment
        self._deadline = _deadline

        super().__init__(timeout=None)

        self.post_title = TextInput(
            label="Job Title",
            placeholder="What's this job about?",
            style=TextStyle.short,
            default=None if not self._title else self._title,
            required=True,
        )

        self.post_desc = TextInput(
            label="Job Description",
            placeholder="Please share job details like responsibilities, experience or any specific qualifications or skills.",
            style=TextStyle.long,
            default=None if not self._desc else self._desc,
            required=True
        )

        self.post_payment = TextInput(
            label="Job Budget",
            placeholder="What's your budget for this job?",
            style=TextStyle.short,
            default=None if not self._payment else self._payment,
            required=True
        )

        self.post_deadline = TextInput(
            label="Job Deadline",
            placeholder="Enter a deadline for your job or N/A.",
            style=TextStyle.short,
            default=None if not self._deadline else self._deadline,
            required=False
        )

        self.add_item(self.post_title)
        self.add_item(self.post_desc)
        self.add_item(self.post_payment)
        self.add_item(self.post_deadline)

    async def on_submit(self, interaction: discord.Interaction):   
        if self.post_deadline.value:
            if not self.post_deadline.value:
                self.post_deadline.value = 'N/A'

        id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(7)]).upper()

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
        post_embed.set_footer(text="Post ID: {}".format(id))
        post_embed.set_image(url=config.PAID_JOB_BANNER_URL)
        insert_paid_job_post(id, interaction.user.id, post_title, post_description, post_payment, post_deadline)

        await interaction.response.send_message(embed=post_embed, view=NotificationSelectorView(), ephemeral=True)

class PostEditModal(Modal, title="Create a Paid Job Post"):
    def __init__(self, _title: str=None, _desc: str=None, _payment: str=None, _deadline: str=None):
        self._title = _title
        self._desc = _desc
        self._payment = _payment
        self._deadline = _deadline

        super().__init__(timeout=None)

        self.post_title = TextInput(
            label="Job Title",
            placeholder="What's this job about?",
            style=TextStyle.short,
            default=None if not self._title else self._title,
            required=True,
        )

        self.post_desc = TextInput(
            label="Job Description",
            placeholder="Please describe your post in detail.",
            style=TextStyle.long,
            default=None if not self._desc else self._desc,
            required=True
        )

        self.post_payment = TextInput(
            label="Job Budget",
            placeholder="What's your budget for this job?",
            style=TextStyle.short,
            default=None if not self._payment else self._payment,
            required=True
        )

        self.post_deadline = TextInput(
            label="Job Deadline",
            placeholder="Enter a deadline for your job or N/A.",
            style=TextStyle.short,
            default=None if not self._deadline else self._deadline,
            required=False
        )

        self.add_item(self.post_title)
        self.add_item(self.post_desc)
        self.add_item(self.post_payment)
        self.add_item(self.post_deadline)

    async def on_submit(self, interaction: discord.Interaction):
        if self.post_deadline.value:
            if not self.post_deadline.value:
                self.post_deadline.value = 'N/A'

        post_id = interaction.message.embeds[0].footer.text[9:]
        data = find_post_by_post_id(post_id)
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
            post_embed.set_image(url=config.PAID_JOB_BANNER_URL)
            
            update_paid_job_post(post_id, post_title, post_description, post_payment, post_deadline)
        
            await interaction.response.edit_message(embed=post_embed, view=NotificationSelectorView())
        
        else:
            await interaction.response.send_message(content="{} An unexpected error occured! `ERROR: INVALID_DATABASE_ENTRY`".format(config.WARN_EMOJI), ephemeral=True)