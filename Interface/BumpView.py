import config
import sqlite3
import discord
import datetime

from discord import ButtonStyle
from discord.ui import Button, View, button
from Functions.DBController import find_out_going_post_by_forum_id, update_out_going_post_bumped_at

class BumpView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @button(label="Bump", emoji="🚀", style=ButtonStyle.blurple, custom_id="bump_post")
    async def bump_btn(self, interaction: discord.Interaction, button: Button):
        data = find_out_going_post_by_forum_id(interaction.channel.id)
        if data:
            post_id = data.post_id
            bumped_at = 0 if not data.bumped_at else int(data.bumped_at)
            user = interaction.guild.get_member(int(data.user_id))
            logs_channel = interaction.guild.get_channel(config.POST_LOGGING_CHANNEL_ID)
            current_time = round(datetime.datetime.now().timestamp())
            message = interaction.channel.get_partial_message(data.message_id)

            if interaction.user == user:
                if int(current_time - bumped_at) >= 115200:
                    await interaction.channel.send(content="Bump!", delete_after=3)
                    update_out_going_post_bumped_at(interaction.channel.id, current_time)
                    await logs_channel.send(embed=discord.Embed(title="Post Bumped", description="**Type:** Manual\n**Author:** {}\n**Post ID:** [{}]({})".format(user.mention, post_id, message.jump_url), color=discord.Color.blue(), timestamp=datetime.datetime.now()))
                    await interaction.response.defer()
                else:
                    future_stamp = current_time + (115200 - (current_time - bumped_at))
                    await interaction.response.send_message(content="{} You can't bump your post!\nCome back <t:{}:R>".format(config.WARN_EMOJI, future_stamp), ephemeral=True)
                    return
            
            else:
                await interaction.response.send_message(content="{} You can't bump someone's post.".format(config.WARN_EMOJI), ephemeral=True)
                return
