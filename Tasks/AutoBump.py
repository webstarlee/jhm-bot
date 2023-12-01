import config
import sqlite3
import discord
import datetime

from discord.ext import commands, tasks

class AutoBump(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = sqlite3.connect("./Databases/posts.sqlite")
        self.auto_bump.start()
    
    @tasks.loop(seconds=1)
    async def auto_bump(self):
        await self.bot.wait_until_ready()
        data = self.database.execute("SELECT post_id, user_id, message_id, forum_id, bumped_at FROM OutgoingPosts").fetchall()
        guild = self.bot.get_guild(config.GUILD_ID)
        logs_channel = guild.get_channel(config.POST_LOGGING_CHANNEL_ID)
        if data:
            for entry in data:
                thread = guild.get_thread(entry[3])
                if thread is not None:
                    message = thread.get_partial_message(entry[2])
                    user = guild.get_member(entry[1])
                    if user is not None:
                        premium_role = guild.get_role(config.PREMIUM_ROLE_ID)
                        vip_role = guild.get_role(config.VIP_ROLE_ID)
                        if premium_role in user.roles or vip_role in user.roles:
                            bumped_at = entry[4]
                            current_time = round(datetime.datetime.now().timestamp())
                            if int(current_time - bumped_at) >= 115200:
                                await thread.send(content="Bump!", delete_after=3)
                                self.database.execute("UPDATE OutgoingPosts SET bumped_at = ? WHERE forum_id = ?", (current_time, thread.id,)).connection.commit()
                                await logs_channel.send(embed=discord.Embed(title="Post Bumped", description="**Type:** Auto\n**Author:** {}\n**Post ID:** [{}]({})".format(user.mention, entry[0], message.jump_url), color=discord.Color.gold(), timestamp=datetime.datetime.now()))
                                return

                            else:
                                pass
                        
                        else:
                            pass
                    
                    else:
                        pass
                else:
                    pass
        else:
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoBump(bot))