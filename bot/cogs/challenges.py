import os
import json
import random
import re

import discord
from discord.ext import commands



class Challenges(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dir = os.path.dirname(__file__)
        self.filename_users = os.path.join(self.dir, '../data/users.json')
        self.debug_mode = False
        self._init_users()
        self._init_challenges()


    @staticmethod
    def read_json(filename):
        with open(filename) as f:
            user_data = json.load(f)
        return user_data


    @staticmethod
    def write_json(data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f, sort_keys=True, indent=4)
        return f


    def _init_users(self):
        self.user_data = self.read_json(self.filename_users)


    def _init_challenges(self):
        filename = os.path.join(self.dir, '../data/tasks_november_2019.json')
        self.challenges = self.read_json(filename)
        
        self.title = self.challenges.get('title', 'MistressSyn Challenges')
        self.host = self.challenges.get("host", 'House of Chastity')
        self.year = self.challenges.get('year', 2019)
        self.subtitle = self.challenges.get('subtitle', 'Daily Challenge')
        self.emoji = self.challenges.get('emoji', 'lock')
        self.thumbnail = self.challenges.get('thumbnail')
        self.desc = self.challenges.get('description', 'Enter description')

        self.authors = self.challenges.get('authors')

        self.tasks = self.challenges.get('tasks')


   #  @commands.Cog.listener()
   #  def on_guild_join(self, guild):
   #      """
   #      This event receives the the guild when the bot joins.
   #      """
   #      print(f'Joined {guild.name} with {guild.member_count} users!')

    def _output_user_data(self):
        try:
            self.write_json(self.user_data, self.filename_users)
        except:
            print('Failed writing user data to .json!')
            print(self.user_data)        


    def _add_user(self, user):
        user_id = str(user.id)
        def_user = {
            'name' : user.name,
            'discriminator' : user.discriminator,
            'nick' : user.nick,
            'cur_challenge' : None
        }

        self.user_data[user_id] = def_user
        self._output_user_data()


    @commands.command()
    async def debug(self, ctx, state):
        self.debug_mode = state.lower() == "true" or state.lower() == "on"
        if self.debug_mode:
            await ctx.send(f"Debug mode is on.")
        else:
            await ctx.send(f"Debug mode is off.")


    # @commands.command()
    # async def show_attrs(self, ctx):
    #     attrs = vars(self)
    #     for k, v in attrs.items():
    #         await ctx.send(f"{k} : {v}")


    @commands.command(aliases=['get'])
    async def get_attr(self, ctx, attr):
        attrs = vars(self)
        if attr in attrs.keys():
            await ctx.send(f"{attr} : {attrs[attr]}")


    @commands.command()
    async def register(self, ctx):
        """
        A test command, Mainly used to show how commands and cogs should be laid out.
        """
        user = ctx.message.author
        if str(user.id) in self.user_data.keys():
            await ctx.send('You are already registered!')
            return False

        self._add_user(user)        
        await ctx.send('Registered!')


    def _set_user_challenge(self, user_id, challenge):
        self.user_data[user_id]['cur_challenge'] = challenge.get('title')
        self._output_user_data()


    def _parse_challenge_desc(self, challenge):
        """ parses description for special formatted functions """
        desc = challenge.get('description')

        # substitutes random integer for "{i-i}""
        pattern = re.compile("{(\d+)-(\d+)}")
        match = pattern.search(desc)
        if match:
            _min, _max = match.group(1, 2)
            rand_int = random.randint(int(_min), int(_max))
            desc = re.sub("{(\d+-\d+)}", str(rand_int), desc )
        
        return desc


    def _show_challenge(self, ctx, challenge, user=None):
        """ Creates message/embed bundle for a challenge """
        msg = ""
        title = challenge.get('title')
        emoji = challenge.get('emoji')
        try:
            thumbnail = challenge.get('thumbnail')
        except KeyError:
            thumnail = self.thumbnail

        desc = self._parse_challenge_desc(challenge)

        reward = challenge.get('reward')
        author = challenge.get('author')

        author_data = self.authors.get(author)
        author_name = author_data.get('name')
        author_id = author_data.get('id')
        author_icon = author_data.get('icon')
        author_url = author_data.get('url')

        if emoji:
            title = f":{emoji}: - {title} - :{emoji}:"

        embed = discord.Embed(title=title, description=desc, color=discord.Colour.from_rgb(255,0,191))

        if author_icon:
            embed.set_author(name=author_name, icon_url=author_icon)
        else:
            embed.set_author(name=author_name)

        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        embed.add_field(name="Reward:", value=reward, inline=False)

        embed.set_footer(text=f"© {self.year} {author_name} - Permissions granted to {self.host}. All rights reserved.")

        if user:
            msg = f'{ctx.author.mention}'
            embed.add_field(name="Assigned To:", value='{}'.format(ctx.author.name), inline=False)

        return msg, embed


    @commands.command(aliases=['c'])
    async def challenge(self, ctx):
        """
        A test command, Mainly used to show how commands and cogs should be laid out.
        """
        user_id = str(ctx.message.author.id)
        if not user_id in self.user_data.keys() and not self.debug_mode:
            # title = 'Not Registered Yet!'
            # desc = f"{ctx.author} has not registered to accept challenges yet.  Use !register now."
            # embed = discord.Embed(title=title, description=desc, color=discord.Colour.from_rgb(255,0,191))
            # await ctx.channel.send(f'{ctx.author.mention}', embed=embed)
            await ctx.send('!register first...')
            return False
        if self.user_data[user_id]['cur_challenge'] and not self.debug_mode:
            await ctx.send('You already have a challenge assigned!')
            return False

        challenge = random.choice(self.tasks)
        self._set_user_challenge(user_id, challenge)

        msg, embed = self._show_challenge(ctx, challenge, user=ctx.message.author)
        await ctx.channel.send(msg, embed=embed)

        # await ctx.send("Here's your challenge:")
        # await ctx.send(f':{emoji}: {name} :{emoji}:')


    @commands.command(aliases=['p'])
    async def punish(self, ctx):
        await ctx.channel.send(f"{ctx.author.mention} must be punished!")


    @commands.command(aliases=['r'])
    async def reward(self, ctx):
        await ctx.channel.send(f"{ctx.author.mention}, you will be rewarded!")


    @commands.command()
    async def points(self, ctx):
        user_id = str(ctx.message.author.id)
        if not user_id in self.user_data.keys():
            await ctx.send('!register first...')
            return False
        points = self.user_data[user_id].get('points')
        await ctx.channel.send(f"{ctx.author.mention}, you have {points}.")


    @commands.command()
    async def complete(self, ctx):
        """
        A test command, Mainly used to show how commands and cogs should be laid out.
        """
        user_id = str(ctx.message.author.id)
        if not user_id in self.user_data.keys():
            await ctx.send('!register first...')
            return False
        if not self.user_data[user_id]['cur_challenge']:
            await ctx.send("You don't have a challenge assigned!")
            return False

        self._set_user_challenge(user_id, challenge=None)
        await ctx.channel.send(f"{ctx.author.mention}, you have completed your challenge and will be rewarded")


    @commands.command()
    async def users(self, ctx):
        print(self.user_data)



def setup(bot):
    bot.add_cog(Challenges(bot))
