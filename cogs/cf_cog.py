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
from database.database import Database


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

        users = Database.fetch_many("SELECT user_id, handle FROM users")
        if len(users) > 0:
            handles = [user[1] for user in users]
            for i, user in enumerate(User.get_users(handles)):
                self.users[users[i][0]] = user
        
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
    
    @staticmethod
    async def remove_roles(bot: Bot):
        for guild in bot.guilds:
            roles = list(CFCog.roles.values())
            roles = [guild.get_role(role) for role in roles]
            roles = [role for role in roles if role is not None]
            for member in guild.members:
                if member.bot:
                    continue

                await member.remove_roles(*roles)
    
    @command(name="register")
    async def register(self, ctx: Context[Bot], handle: str):
        ctx_mgr().set_init_context(ctx)

        if ctx.author.id in self.users:
            await ctx.reply("You are already registered.")
            return
        
        self.users[ctx.author.id] = User(handle)
        query = "INSERT INTO users (user_id, handle) VALUES (%s, %s)"
        Database.execute_query(query, ctx.author.id, handle)
        await send_message(content="You have been registered!")
    
    @command(name="unregister")
    async def unregister(self, ctx: Context[Bot]):
        ctx_mgr().set_init_context(ctx)

        if ctx.author.id not in self.users:
            await ctx.reply("You are not registered.")
            return
        
        del self.users[ctx.author.id]
        query = "DELETE FROM users WHERE user_id = %s"
        Database.execute_query(query, ctx.author.id)
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

    @command(name="help")
    async def help(self, ctx: Context[Bot]):
        ctx_mgr().set_init_context(ctx)

        embed = BaseEmbed(title="Help")
        embed.add_field(name="General Commands", value="- $ping\nResponds with alternating 'Ping!' and 'Pong!' messages. No arguments required.\n- $query {question}\nQueries the Gemini API with your question and returns a response. Takes one argument: question.\n- $pm\nSends a private message to you asking how the bot can help and you can talk to it. No arguments required.\n- $gemini enable\nEnables Gemini to respond to every message in the server. No arguments required.\n- $gemini disable\nDisables Gemini from responding to every message in the server. No arguments required.\n- $register {name}\nRegisters a new user. Takes the name of the user\n- !help {question}\nTo ask a question related to the commands to the bot. Takes one optional argument: question.")
        embed.add_field(name="User Management Commands", value="- $register {handle}\nRegisters a new user with the specified Codeforces handle. Takes one argument: handle.\n- $unregister\nUnregisters the current user. No arguments required.\n- $get_details\nRetrieves and displays the registered user's details. No arguments required.")
        embed.add_field(name="Graph Commands", value="- $rating_graph\nDisplays the user's rating graph. No arguments required.\n- $rating_change_graph\nDisplays the user's rating change graph. No arguments required.\n- $rating_comparison_graph {handle1} {handle2} ...\nCompares the rating graphs of multiple users. Takes multiple arguments: handles.\n- $rating_change_comparison_graph {handle1} {handle2} ...\nCompares the rating change graphs of multiple users. Takes multiple arguments: handles.\n- $subs_verdict_graph\nDisplays the user's submissions verdict graph. No arguments required.")
        embed.add_field(name="Role Management Commands", value="- $assign_roles\nAssigns roles to users based on their Codeforces rank. No arguments required.")
        embed.add_field(name="Problem Management Commands", value="- $get_problems\nLoads and displays the count of available problems. No arguments required.\n- $recommend_problem\nRecommends a problem based on the user's rating. No arguments required.")
        embed.add_field(name="Leaderboard Commands", value="- $leaderboard\nDisplays the leaderboard sorted by user ratings. No arguments required.\n- $solved_leaderboard\nDisplays the leaderboard sorted by the number of problems solved. No arguments required.\n- $max_rating_leaderboard\nDisplays the leaderboard sorted by users' maximum ratings. No arguments required.")
        embed.add_field(name="Note", value="Ensure you are registered to use most of the commands. Use $register to register yourself with your Codeforces handle.")
        await send_message(embed=embed)
    