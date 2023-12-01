import config
import discord

from discord import ButtonStyle
from discord.ui import View, Button, button
from Interface.VIPPostView import VIPPostModal
from Interface.ForHireView import ForHireModal
from Interface.PaidJobPostView import PostModal
from Interface.UnpaidJobPostView import UnpaidJobModal
from Interface.CommissionPostView import CommissionModal

class EmbedView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @button(label="Post a Paid Job", emoji='💼', style=ButtonStyle.blurple, custom_id="paid_job_button", row=0)
    async def paid_job_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(PostModal())

    @button(label="Post a Commission Job", emoji='💰', style=ButtonStyle.blurple, custom_id="commission_job_button", row=0)
    async def commission_job_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(CommissionModal())

    @button(label="Post a For-Hire Ad", emoji='📝', style=ButtonStyle.blurple, custom_id="for_hire_button", row=1)
    async def for_hire_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ForHireModal())
        
    @button(label="Post an Unpaid Job", emoji='🤝', style=ButtonStyle.blurple, custom_id="unpaid_job_button", row=1)
    async def unpaid_job_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(UnpaidJobModal())
    
    @button(label="--------------------- [VIP ONLY] ---------------------", style=ButtonStyle.gray, disabled=True, custom_id="vip_line_break_btn", row=2)
    async def vip_line_break_btn(self, interaction: discord.Interaction, button: Button):
        return
    
    @button(label="Create Special Post", style=ButtonStyle.blurple, emoji="💎", custom_id="special_post_button", row=3)
    async def special_post_btn(self, interaction: discord.Interaction, button: Button):
        vip_role = interaction.guild.get_role(config.VIP_ROLE_ID)
        if vip_role in interaction.user.roles:
            await interaction.response.send_modal(VIPPostModal())

        else:
            await interaction.response.send_message(content="{} You aren't a **VIP** subscriber.".format(config.WARN_EMOJI), ephemeral=True)
            return