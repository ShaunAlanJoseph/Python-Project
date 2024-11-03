from discord.ext import commands, tasks
from discord.ext.commands import command, Bot, Cog, Context  # type: ignore
from discord import File
from typing import Any, Dict, List
from logging import info, error as err
from utils.context_manager import ctx_mgr
from codeforces.user import User
from codeforces.problem import Problem, get_problems
from utils.discord import send_message, BaseEmbed
import random
from asyncio import sleep


class CFCog(Cog):
    users: Dict[int, User] = {}

    roles = {
        "newbie": 1302740866724794510,
        "pupil": 1302741628817244270,
        "specialist": 1302741683988992081,
        "expert": 1302741730705014879
    }

    problems: List[Problem] = []
    
    def __init__(self, bot: Bot):
        self.bot = bot
        info("CF Bot has been loaded.")

    async def cog_command_error(self, ctx: Context[Any], error: Exception) -> None:
        if isinstance(error, commands.CheckFailure):
            return
        err(f"An excpetion occured: {error}", exc_info=True)
    
    @command(name="ping")
    async def ping(self, ctx: Context[Bot]):
        ctx_mgr().set_init_context(ctx)
        
        from asyncio import sleep
        from utils.discord import send_message, BaseEmbed

        embed1 = BaseEmbed(title="Ping!")
        await send_message(content="Pong!", embed=embed1)
        await sleep(3)
        embed2 = BaseEmbed(title="Pong!")
        await send_message(content="Ping!", embed=embed2)
        await sleep(3)
        embed3 = BaseEmbed(title="Ping!")
        await send_message(content="Pong!", embed=embed3)
    
    @command(name="register")
    async def register(self, ctx: Context[Bot], handle: str):
        ctx_mgr().set_init_context(ctx)

        if ctx.author.id in self.users:
            await ctx.reply("You are already registered.")
            return
        
        self.users[ctx.author.id] = User(handle)
        await send_message(content="You have been registered!")
    
    @command(name="unregister")
    async def unregister(self, ctx: Context[Bot]):
        ctx_mgr().set_init_context(ctx)

        if ctx.author.id not in self.users:
            await ctx.reply("You are not registered.")
            return
        
        del self.users[ctx.author.id]
        await send_message(content="You have been unregistered!")

        assert ctx.author is not None
        await ctx.author.remove_roles(*ctx.author.roles[1:])  # type: ignore
    
    @command(name="get_details")
    async def get_details(self, ctx: Context[Bot]):
        ctx_mgr().set_init_context(ctx)

        if ctx.author.id not in self.users:
            await ctx.reply("You are not registered.")
            return
        
        user = self.users[ctx.author.id]
        embed = user.get_user_details_embed()
        await send_message(embed=embed)
    
    @command(name="rating_graph")
    async def rating_graph(self, ctx: Context[Bot]):
        ctx_mgr().set_init_context(ctx)

        if ctx.author.id not in self.users:
            await ctx.reply("You are not registered.")
            return

        user = self.users[ctx.author.id]
        image = user.get_user_rating_graph()
        file = File(image, filename="rating_graph.png")
        embed = BaseEmbed(title="Rating Graph")
        await send_message(file=file, embed=embed)
    
    @command(name="rating_change_graph")
    async def rating_change_graph(self, ctx: Context[Bot]):
        ctx_mgr().set_init_context(ctx)

        if ctx.author.id not in self.users:
            await ctx.reply("You are not registered.")
            return
        
        user = self.users[ctx.author.id]
        image = user.get_user_rating_change_graph()
        file = File(image, filename="rating_change_graph.png")
        embed = BaseEmbed(title="Rating Change Graph")
        await send_message(file=file, embed=embed)
    
    @command(name="rating_comparison_graph")
    async def rating_comparison_graph(self, ctx: Context[Bot], *args: str):
        ctx_mgr().set_init_context(ctx)

        if ctx.author.id not in self.users:
            await ctx.reply("You are not registered.")
            return
        
        user = self.users[ctx.author.id]
        users = User.get_users(list(args))
        image = user.get_user_rating_comparison_graph(users)
        file = File(image, filename="rating_comparison_graph.png")
        embed = BaseEmbed(title="Rating Comparison Graph")
        await send_message(file=file, embed=embed)
    
    @command(name="rating_change_comparison_graph")
    async def rating_change_comparison_graph(self, ctx: Context[Bot], *args: str):
        ctx_mgr().set_init_context(ctx)

        if ctx.author.id not in self.users:
            await ctx.reply("You are not registered.")
            return
        
        user = self.users[ctx.author.id]
        users = User.get_users(list(args))
        image = user.get_user_rating_change_comparison_graph(users)
        file = File(image, filename="rating_change_comparison_graph.png")
        embed = BaseEmbed(title="Rating Change Comparison Graph")
        await send_message(file=file, embed=embed)
    
    @command(name="subs_verdict_graph")
    async def subs_verdict_graph(self, ctx: Context[Bot]):
        ctx_mgr().set_init_context(ctx)

        if ctx.author.id not in self.users:
            await ctx.reply("You are not registered.")
            return
        
        user = self.users[ctx.author.id]
        image = user.get_user_subs_verdict_graph()
        file = File(image, filename="subs_verdict_graph.png")
        embed = BaseEmbed(title="Submissions Verdict Graph")
        await send_message(file=file, embed=embed)
    
    @command(name="assign_roles")
    async def assign_role(self, ctx: Context[Bot]):
        ctx_mgr().set_init_context(ctx)

        for user_id, user in self.users.items():
            rank = "newbie" if user.rank is None else user.rank
            role = self.roles[rank]
            assert ctx.guild is not None
            role = ctx.guild.get_role(role)
            user = ctx.guild.get_member(user_id)
            assert user is not None
            assert role is not None
            await user.add_roles(role)
    
    @command(name="get_problems")
    async def get_problems(self, ctx: Context[Bot]):
        ctx_mgr().set_init_context(ctx)

        self.problems, _ = get_problems()

        embed = BaseEmbed(title="Loaded Problems")
        embed.add_field(name="Count", value=str(len(self.problems)))
        await send_message(embed=embed)

    @command(name="recommend_problem")
    async def recommend_problem(self, ctx: Context[Bot]):
        ctx_mgr().set_init_context(ctx)

        if not self.problems:
            await ctx.reply("Problems not loaded.")
            return
        
        if ctx.author.id not in self.users:
            await ctx.reply("You are not registered.")
            return
        
        rating = self.users[ctx.author.id].rating
        if rating is None:
            rating = 800
        
        problems = [problem for problem in self.problems if problem.rating is not None and rating + 200 <= problem.rating <= rating + 300]
        if not problems:
            await ctx.reply("No problems found.")
            return

        problem = random.choice(problems)
        embed = problem.get_problem_embed()
        await send_message(embed=embed)

    @command(name="leaderboard")
    async def leaderboard(self, ctx: Context[Bot]):
        ctx_mgr().set_init_context(ctx)

        embed = BaseEmbed(title="Leaderboard")
        users = list(self.users.values())
        users.sort(key=lambda user: user.rating, reverse=True)  # type: ignore
        for i, user in enumerate(users):
            embed.add_field(name=f"{i + 1}. {user.handle}", value=f"Rating: {user.rating}")
        await send_message(embed=embed)
    
    @command(name="solved_leaderboard")
    async def solved_leaderboard(self, ctx: Context[Bot]):
        ctx_mgr().set_init_context(ctx)

        user_solves = {}
        for _, user in self.users.items():
            user.load_submissions()
            user_solves[user.handle] = 0
            assert user.submissions is not None
            for submission in user.submissions:
                if submission.verdict == "OK":
                    user_solves[user.handle] += 1
            await sleep(2) 

        embed = BaseEmbed(title="Solved Leaderboard")
        users = list(self.users.values())
        users.sort(key=lambda user: user_solves[user.handle], reverse=True)  # type: ignore
        for i, user in enumerate(users):
            embed.add_field(name=f"{i + 1}. {user.handle}", value=f"Solved: {user_solves[user.handle]}")
        await send_message(embed=embed)
    
    @command(name="max_rating_leaderboard")
    async def max_rating_leaderboard(self, ctx: Context[Bot]):
        ctx_mgr().set_init_context(ctx)

        embed = BaseEmbed(title="Max Rating Leaderboard")
        users = list(self.users.values())
        users.sort(key=lambda user: user.maxRating, reverse=True)  # type: ignore
        for i, user in enumerate(users):
            embed.add_field(name=f"{i + 1}. {user.handle}", value=f"Max Rating: {user.maxRating}")
        await send_message(embed=embed)

    @tasks.loop(hours=1)
    async def update_users(self):
        handles = [user.handle for user in self.users.values()]
        handles_to_ids = {user.handle: user_id for user_id, user in self.users.items()}
        for user in User.get_users(handles):
            self.users[handles_to_ids[user.handle]] = user
        
        for user_id, user in self.users.items():
            rank = "newbie" if user.rank is None else user.rank
            for guild in self.bot.guilds:
                role = self.roles[rank]
                role = guild.get_role(role)
                user = guild.get_member(user_id)
                assert user is not None
                assert role is not None
                await user.add_roles(role)
    