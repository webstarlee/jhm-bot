import os
import config
import sqlite3
import discord

from discord.ext import commands
from Interface.BumpView import BumpView
from Interface.GenerateEmbedView import EmbedView
from Interface.PostApprovalView import PostApprovalView
from Interface.JobPostView import PostView, ForHirePostView, PaidJobPostView

intents = discord.Intents.all()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=config.PREFIX,
            intents=intents,
            application_id=config.APPLICATION_ID,
            activity=discord.Activity(type=discord.ActivityType.watching, name="community")
        )

    async def setup_hook(self):
        
        sqlite3.connect("./Databases/posts.sqlite").execute(
            '''
                CREATE TABLE IF NOT EXISTS Posts (
                    post_id TEXT,
                    user_id INTEGER,
                    posted_at INTEGER,
                    post_title TEXT,
                    post_desc TEXT,
                    post_payment TEXT,
                    post_deadline TEXT,
                    status TEXT,
                    post_type TEXT,
                    ping_role INTEGER,
                    PRIMARY KEY (post_id)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS IncomingPosts (
                    post_id TEXT,
                    user_id INTEGER,
                    message_id INTEGER,
                    PRIMARY KEY (post_id)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS OutgoingPosts (
                    post_id TEXT,
                    user_id INTEGER,
                    approved_by INTEGER,
                    message_id INTEGER,
                    channel_id INTEGER,
                    forum_id INTEGER,
                    bumped_at INTEGER,
                    PRIMARY KEY (post_id)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS PostReports (
                    post_id TEXT,
                    report_msg INTEGER,
                    reported_by INTEGER,
                    reported_at INTEGER,
                    report_status TEXT,
                    PRIMARY KEY (report_msg)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS ReportThreads (
                    report_msg INTEGER,
                    channel_id INTEGER,
                    thread_id INTEGER,
                    PRIMARY KEY (report_msg)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS JobApplicants (
                    post_id INTEGER,
                    user_id INTEGER,
                    status TEXT
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS Reviews (
                    freelancer_id INTEGER,
                    client_id INTEGER,
                    category TEXT,
                    stars INTEGER,
                    review TEXT
                )
            '''
        )

        self.add_view(BumpView())
        self.add_view(PostView())
        self.add_view(EmbedView())
        self.add_view(PaidJobPostView())
        self.add_view(ForHirePostView())
        self.add_view(PostApprovalView())

        for filename in os.listdir("./Commands"):
            if filename.endswith('.py'):
                await self.load_extension('Commands.{}'.format(filename[:-3]))
                print("Loaded {}".format(filename))

            if filename.startswith('__'):
                pass

        # for filename in os.listdir("./Events"):
        #     if filename.endswith('.py'):
        #         await self.load_extension('Events.{}'.format(filename[:-3]))
        #         print("Loaded {}".format(filename))

        #     if filename.startswith('__'):
        #         pass

        for filename in os.listdir("./Tasks"):
            if filename.endswith('.py'):
                await self.load_extension('Tasks.{}'.format(filename[:-3]))
                print("Loaded {}".format(filename))

            if filename.startswith('__'):
                pass

        await bot.tree.sync()

bot = Bot()

@bot.event
async def on_ready():
    print("{} is online! Latency: {}ms".format(bot.user.name, round(bot.latency * 1000)))

@bot.command(name="reload")
async def _reload(ctx: commands.Context, folder: str, cog: str):
    await ctx.message.delete()
    try:
        await bot.reload_extension(f"{folder}.{cog}")
        await ctx.send("🔁 **{}.py** successfully reloaded!".format(cog))
    except:
        await ctx.send("⚠ Unable to reload **{}**".format(cog))

bot.run(config.TOKEN)