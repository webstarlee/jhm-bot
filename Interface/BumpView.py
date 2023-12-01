import config
import sqlite3
import discord
import datetime

from discord import ButtonStyle
from discord.ui import Button, View, button

database = sqlite3.connect("./Databases/posts.sqlite")

class BumpView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @button(label="Bump", emoji="🚀", style=ButtonStyle.blurple, custom_id="bump_post")
    async def bump_btn(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT post_id, user_id, message_id, bumped_at FROM OutgoingPosts WHERE forum_id = ?", (interaction.channel.id,)).fetchone()
        if data:
            post_id = data[0]
            bumped_at = 0 if not data[1] else int(data[3])
            user = interaction.guild.get_member(int(data[1]))
            logs_channel = interaction.guild.get_channel(config.POST_LOGGING_CHANNEL_ID)
            current_time = round(datetime.datetime.now().timestamp())
            message = interaction.channel.get_partial_message(data[2])

            if interaction.user == user:
                if int(current_time - bumped_at) >= 115200:
                    await interaction.channel.send(content="Bump!", delete_after=3)
                    database.execute("UPDATE OutgoingPosts SET bumped_at = ? WHERE forum_id = ?", (current_time, interaction.channel.id,)).connection.commit()
                    await logs_channel.send(embed=discord.Embed(title="Post Bumped", description="**Type:** Manual\n**Author:** {}\n**Post ID:** [{}]({})".format(user.mention, post_id, message.jump_url), color=discord.Color.blue(), timestamp=datetime.datetime.now()))
                    await interaction.response.defer()
                else:
                    future_stamp = current_time + (115200 - (current_time - bumped_at))
                    await interaction.response.send_message(content="{} You can't bump your post!\nCome back <t:{}:R>".format(config.WARN_EMOJI, future_stamp), ephemeral=True)
                    return
            
            else:
                await interaction.response.send_message(content="{} You can't bump someone's post.".format(config.WARN_EMOJI), ephemeral=True)
                return
