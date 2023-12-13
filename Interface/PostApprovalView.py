import config
import sqlite3
import discord
import datetime

from Interface.BumpView import BumpView
from discord import ButtonStyle, TextStyle
from discord.ui import View, Modal, TextInput, Button, button
from Interface.JobPostView import PostView, ForHirePostView, PaidJobPostView
from Functions.DBController import (
    find_incoming_post,
    find_post_by_post_id,
    incoming_post_remove,
    insert_out_going_post,
    update_for_fire_post_status
)

database = sqlite3.connect("./Databases/posts.sqlite")

class PostApprovalView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @button(label="Approve", style=ButtonStyle.green, custom_id="approve_button")
    async def approve_btn(self, interaction: discord.Interaction, button: Button):
        incoming_post = find_incoming_post(interaction.message.id)
        post_data = find_post_by_post_id(incoming_post.post_id)
        post_id = post_data.post_id
        post_author = interaction.guild.get_member(post_data.user_id)
        post_title = post_data.post_title
        post_description = post_data.post_desc
        post_portfolio = "N/A" if not post_data.post_portfolio else post_data.post_portfolio
        post_payment = post_data.post_payment.capitalize() if post_data.post_payment else "N/A"
        post_deadline = "N/A" if not post_data.post_deadline else post_data.post_deadline
        post_type = post_data.post_type
        ping_role = interaction.guild.get_role(post_data.ping_role)

        if post_type == 'paid':
            paid_jobs_channel = interaction.guild.get_channel(config.PAID_JOBS_CHANNEL_ID)
            logging_channel = interaction.guild.get_channel(config.APPROVAL_LOGGING_CHANNEL_ID)
            
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
                name=f"{config.ID_TEST} Client:",
                value=f"{config.TOP_TO_RIGHT_EMOJI} {post_author.mention}",
                inline=True
            )
            post_embed.set_footer(text="Post ID: {}".format(post_id))
            post_embed.set_image(url=config.PAID_JOB_BANNER_URL)

            self.approve_btn.disabled = True
            self.approve_btn.label = "Approved"
            self.reject_btn.disabled = True
            self.reject_btn.style = ButtonStyle.gray

            await interaction.response.edit_message(view=self)
            post_msg = await paid_jobs_channel.send(content=f"Notification:: {ping_role.mention}", embed=post_embed, view=PaidJobPostView())
            incoming_post_remove(post_id)
            insert_out_going_post(post_id, post_author.id, interaction.user.id, post_msg.id, "NULL")
            update_for_fire_post_status(post_id, "approved")
            try:
                # await post_author.send(content="{} Your post **[{}]({})** has been approved.".format(config.DONE_EMOJI, post_title, post_msg.jump_url))
                message = "{} Your post **[{}](<{}>)** has been approved.".format(config.DONE_EMOJI, post_title, post_msg.jump_url)
                await post_author.send(content=f"{message}")
            except:
                await interaction.followup.send(content="{} Unable to DM {}!".format(config.WARN_EMOJI, post_author.mention))

            await logging_channel.send(embed=discord.Embed(title="Post Approved", description=f"**Posted By:** {post_author.mention}\n**Post Type:** Paid Job\n**Approved By:** {interaction.user.mention}\n**Post Link:** {post_msg.jump_url}", color=discord.Color.green()))
        
        if post_type == 'forhire':
            for_hire_forum = interaction.guild.get_channel(config.FOR_HIRE_FORUM_ID)
            logging_channel = interaction.guild.get_channel(config.APPROVAL_LOGGING_CHANNEL_ID)

            post_embed = discord.Embed(
                title=f"{config.PERSON_EMOJI} {post_title}",
                description=f"{config.INVISIBLE_CHARACTER}\n{config.DESCRIPTION_EMOJI} **Description:**\n{config.TOP_TO_RIGHT_EMOJI} {post_description}\n{config.INVISIBLE_CHARACTER}",
                color=config.JHM_BLUE
            )
            post_embed.add_field(
                name=f"{config.INFO_EMOJI} Portfolio:",
                value=f"{config.TOP_TO_RIGHT_EMOJI} {post_portfolio}\n{config.INVISIBLE_CHARACTER}",
                inline=False
            )
            post_embed.add_field(
                name=f"{config.CARD_EMOJI} Payment Method:",
                value=f"{config.TOP_TO_RIGHT_EMOJI} {post_payment}",
                inline=True
            )
            post_embed.add_field(
                name=f"{config.ID_TEST} Freelancer:",
                value=f"{config.TOP_TO_RIGHT_EMOJI} {post_author.mention}",
                inline=True
            )
            post_embed.set_footer(text="Post ID: {}".format(post_id))
            post_embed.set_image(url=config.FOR_HIRE_BANNER_URL)

            self.approve_btn.disabled = True
            self.approve_btn.label = "Approved"
            self.reject_btn.disabled = True
            self.reject_btn.style = ButtonStyle.gray

            post_tags = []
            for tag in for_hire_forum.available_tags:
                if tag.name.lower() in ping_role.name.lower():
                        post_tags.append(tag)

            forum_thread = await for_hire_forum.create_thread(name=post_title, embed=post_embed, applied_tags=post_tags, view=ForHirePostView())
            await forum_thread.thread.send(view=BumpView())

            await interaction.response.edit_message(view=self)
            incoming_post_remove(post_id)
            insert_out_going_post(post_id, post_author.id, interaction.user.id, forum_thread.message.id, forum_thread.thread.id)
            update_for_fire_post_status(post_id, "approved")
            try:
                await post_author.send(content="{} Your post **[{}]({})** has been approved.".format(config.DONE_EMOJI, post_title, forum_thread.message.jump_url))
            except:
                await interaction.followup.send(content="{} Unable to DM {}!".format(config.WARN_EMOJI, post_author.mention), ephemeral=True)

            await logging_channel.send(embed=discord.Embed(title="Post Approved", description=f"**Posted By:** {post_author.mention}\n**Post Type:** For Hire Post\n**Approved By:** {interaction.user.mention}\n**Post Link:** {forum_thread.message.jump_url}", color=discord.Color.green()))

        if post_type == 'unpaid':
            unpaid_jobs_forum = interaction.guild.get_channel(config.UNPAID_JOB_FORUM_ID)
            logging_channel = interaction.guild.get_channel(config.APPROVAL_LOGGING_CHANNEL_ID)

            post_embed = discord.Embed(
                title=f"{config.PERSON_EMOJI} {post_title}",
                description=f"{config.INVISIBLE_CHARACTER}\n{config.DESCRIPTION_EMOJI} **Description:**\n{config.TOP_TO_RIGHT_EMOJI} {post_description}\n{config.INVISIBLE_CHARACTER}",
                color=config.JHM_BLUE
            )
            post_embed.add_field(
                name=f"{config.CLOCK_EMOJI} Deadline:",
                value=f"{config.TOP_TO_RIGHT_EMOJI} {post_deadline}",
                inline=True
            )
            post_embed.add_field(
                name=f"{config.ID_TEST} Client:",
                value=f"{config.TOP_TO_RIGHT_EMOJI} {post_author.mention}",
                inline=True
            )
            post_embed.set_footer(text="Post ID: {}".format(post_id))
            post_embed.set_image(url=config.UNPAID_JOB_BANNER_URL)

            post_tags = []
            for tag in unpaid_jobs_forum.available_tags:
                if tag.name.lower() in ping_role.name.lower():
                        post_tags.append(tag)

            forum_thread = await unpaid_jobs_forum.create_thread(name=post_title, applied_tags=post_tags, embed=post_embed)
            await forum_thread.thread.send(view=BumpView())

            self.approve_btn.disabled = True
            self.approve_btn.label = "Approved"
            self.reject_btn.disabled = True
            self.reject_btn.style = ButtonStyle.gray

            await interaction.response.edit_message(view=self)
            incoming_post_remove(post_id)
            insert_out_going_post(post_id, post_author.id, interaction.user.id, forum_thread.message.id, forum_thread.thread.id)
            update_for_fire_post_status(post_id, "approved")
            await logging_channel.send(embed=discord.Embed(title="Post Approved", description=f"**Posted By:** {post_author.mention}\n**Post Type:** Unpaid Job\n**Approved By:** {interaction.user.mention}\n**Post Link:** {forum_thread.thread.jump_url}", color=discord.Color.green()))

        if post_type == 'commission':
            commission_jobs_forum = interaction.guild.get_channel(config.COMMISSION_JOB_FORUM_ID)
            logging_channel = interaction.guild.get_channel(config.APPROVAL_LOGGING_CHANNEL_ID)

            post_embed = discord.Embed(
                title=f"{config.PERSON_EMOJI} {post_title}",
                description=f"{config.INVISIBLE_CHARACTER}\n{config.DESCRIPTION_EMOJI} **Description:**\n{config.TOP_TO_RIGHT_EMOJI} {post_description}\n{config.INVISIBLE_CHARACTER}",
                color=config.JHM_BLUE
            )
            post_embed.add_field(
                name=f"{config.CARD_EMOJI} Payment:",
                value=f"{config.TOP_TO_RIGHT_EMOJI} {post_payment}",
                inline=True
            )
            post_embed.add_field(
                name=f"{config.CLOCK_EMOJI} Deadline:",
                value=f"{config.TOP_TO_RIGHT_EMOJI} {post_deadline}",
                inline=True
            )
            post_embed.add_field(
                name=f"{config.ID_TEST} Client:",
                value=f"{config.TOP_TO_RIGHT_EMOJI} {post_author.mention}",
                inline=True
            )
            post_embed.set_footer(text="Post ID: {}".format(post_id))
            post_embed.set_image(url=config.COMMISSION_JOB_BANNER_URL)

            post_tags = []
            for tag in commission_jobs_forum.available_tags:
                if tag.name.lower() in ping_role.name.lower():
                        post_tags.append(tag)

            forum_thread = await commission_jobs_forum.create_thread(name=post_title, embed=post_embed, view=PostView(), applied_tags=post_tags)
            await forum_thread.thread.send(view=BumpView())

            self.approve_btn.disabled = True
            self.approve_btn.label = "Approved"
            self.reject_btn.disabled = True
            self.reject_btn.style = ButtonStyle.gray

            await interaction.response.edit_message(view=self)
            incoming_post_remove(post_id)
            insert_out_going_post(post_id, post_author.id, interaction.user.id, forum_thread.message.id, forum_thread.thread.id)
            update_for_fire_post_status(post_id, "approved")
            await logging_channel.send(embed=discord.Embed(title="Post Approved", description=f"**Posted By:** {post_author.mention}\n**Post Type:** Commission\n**Approved By:** {interaction.user.mention}\n**Post Link:** {forum_thread.thread.jump_url}", color=discord.Color.green()))

    @button(label="Reject", style=ButtonStyle.red, custom_id="reject_button")
    async def reject_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(PostRejectModal(self))

class PostRejectModal(Modal, title="Post Reject Modal"):
    def __init__(self, original_view: PostApprovalView):
        self.original_view = original_view
        super().__init__(timeout=None)

    reason = TextInput(
        label="Reason",
        placeholder="State the reason of why you are rejecting this post.",
        style=TextStyle.long,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        incoming_post = find_incoming_post(interaction.message.id)
        post_data = find_post_by_post_id(incoming_post.post_id)
        post_id = post_data.post_id
        post_author = interaction.guild.get_member(post_data.user_id)
        update_for_fire_post_status(post_id, "rejected")

        logging_channel = interaction.guild.get_channel(config.APPROVAL_LOGGING_CHANNEL_ID)

        self.original_view.approve_btn.disabled = True
        self.original_view.approve_btn.style = ButtonStyle.gray
        self.original_view.reject_btn.disabled = True
        self.original_view.reject_btn.label = "Rejected"

        try:
            await post_author.send(content=f"Your post **{post_data[1]}** has been rejected!\n**Reason:** {self.reason}")
        except:
            pass

        await logging_channel.send(embed=discord.Embed(title="Post Rejected", description=f"**Posted By:** {post_author.mention}\n**Rejected By:** {interaction.user.mention}\n**Reason:** {self.reason.value}", color=discord.Color.red()))
        await interaction.response.edit_message(view=self.original_view)