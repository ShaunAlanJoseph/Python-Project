from config import Gemini_API_Key
from discord.ext import commands
import google.generativeai as genai
import time

helpContext='''
Below is the list of available commands for the Codeforces Discord Bot:

General Commands:
- $ping  
  Responds with alternating "Ping!" and "Pong!" messages. No arguments required
- $query {question}  
  Queries the Gemini API with your question and returns a response. Takes one argument: question.
- $pm  
  Sends a private message to you asking how the bot can help and you can talk to it. No arguments required.
- $gemini enable  
  Enables Gemini to respond to every message in the server. No arguments required.
- $gemini disable  
  Disables Gemini from responding to every message in the server. No arguments required.
- $register {name}  
  Registers a new user. Takes the name of the user
- !help {question}  
  To ask a question related to the commands to the bot. Takes one optional argument: question.


User Management Commands:
- $register {handle}  
  Registers a new user with the specified Codeforces handle. Takes one argument: handle.
- $unregister  
  Unregisters the current user. No arguments required.
- $get_details  
  Retrieves and displays the registered user's details. No arguments required.

Graph Commands:
- $rating_graph  
  Displays the user's rating graph. No arguments required.
- $rating_change_graph  
  Displays the user's rating change graph. No arguments required.
- $rating_comparison_graph {handle1} {handle2} ...  
  Compares the rating graphs of multiple users. Takes multiple arguments: handles.
- $rating_change_comparison_graph {handle1} {handle2} ...  
  Compares the rating change graphs of multiple users. Takes multiple arguments: handles.
- $subs_verdict_graph  
  Displays the user's submissions verdict graph. No arguments required.

Role Management Commands:
- $assign_roles  
  Assigns roles to users based on their Codeforces rank. No arguments required.

Problem Management Commands:
- $get_problems  
  Loads and displays the count of available problems. No arguments required.
- $recommend_problem  
  Recommends a problem based on the user's rating. No arguments required.

Leaderboard Commands:
- $leaderboard  
  Displays the leaderboard sorted by user ratings. No arguments required.
- $solved_leaderboard  
  Displays the leaderboard sorted by the number of problems solved. No arguments required.
- $max_rating_leaderboard  
  Displays the leaderboard sorted by users' maximum ratings. No arguments required.

Note: Ensure you are registered to use most of the commands. Use $register to register yourself with your Codeforces handle.
'''


genai.configure(api_key=Gemini_API_Key)
DISCORD_MAX_MESSAGE_LENGTH=2000
PLEASE_TRY_AGAIN_ERROR_MESSAGE='There was an issue with your question please try again.. '
Gemini=False
first_time=True
class GeminiAgent(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
        self.model = genai.GenerativeModel('gemini-pro')

    @commands.Cog.listener()
    async def on_message(self,msg):
        try:
            if msg.content == "ping gemini-agent":
                await msg.channel.send("Agent is connected..")
            elif msg.content[:5] == "!help":
                 prompt=msg.content[5:]
                 global helpContext
                 response = self.gemini_generate_content(helpContext+prompt)
                 await self.send_message_in_chunks(msg.channel,response)
            elif 'Direct Message' in str(msg.channel) and not msg.author.bot:
                response = self.gemini_generate_content(msg.content)
                dmchannel = await msg.author.create_dm()
                await self.send_message_in_chunks(dmchannel,response) 
                global first_time
            elif(not msg.author.bot and Gemini):
                if first_time:
                    await msg.channel.send('Hi, I am Gemini Agent. How can I help you today?')
                    first_time=False
                else:
                    if(msg.content[0]!='$'):
                        response = self.gemini_generate_content(msg.content)
                        await self.send_message_in_chunks(msg.channel,response) 
        except Exception as e:
            await msg.channel.send("There was an error from serverside.. Please try again..")
        

    @commands.command()
    async def query(self,ctx,*,question):
        try:
            response = self.gemini_generate_content(question)
            await self.send_message_in_chunks(ctx,response)
            
        except Exception as e:
            await ctx.send("There was an error from serverside.. Please try again..")
    
    @commands.group()
    async def gemini(self,ctx):
        pass

    @gemini.command()
    async def enable(self,ctx):
        global Gemini,first_time
        Gemini=True
        await ctx.send('Gemini Agent is enabled..')
    
    @gemini.command()
    async def disable(self,ctx):
        global Gemini,first_time
        Gemini=False
        first_time=True
        await ctx.send('Gemini Agent is disabled..')

    @commands.command()
    async def pm(self,ctx):
        dmchannel = await ctx.author.create_dm()
        await dmchannel.send('Hi how can I help you today?')

    def gemini_generate_content(self, content, retries=4, delay=2):
        attempt = 0
        while attempt < retries:
            try:
                response = self.model.generate_content(content, stream=True)
                return response
            except Exception as e:
                print(f"Attempt {attempt + 1}: error in gemini_generate_content:", e)
                if attempt < retries - 1:
                    time.sleep(delay)
                attempt += 1
                return PLEASE_TRY_AGAIN_ERROR_MESSAGE + str(e)
        
    async def send_message_in_chunks(self,ctx,response):
        message = ""
        for chunk in response:
            message += chunk.text
            if len(message) > DISCORD_MAX_MESSAGE_LENGTH:
                extraMessage = message[DISCORD_MAX_MESSAGE_LENGTH:]
                message = message[:DISCORD_MAX_MESSAGE_LENGTH]
                await ctx.send(message)
                message = extraMessage
        if len(message) > 0:
            while len(message) > DISCORD_MAX_MESSAGE_LENGTH:
                extraMessage = message[DISCORD_MAX_MESSAGE_LENGTH:]
                message = message[:DISCORD_MAX_MESSAGE_LENGTH]
                await ctx.send(message)
                message = extraMessage
            await ctx.send(message)
