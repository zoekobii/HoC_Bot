import json
from pathlib import Path
import random
import re

import discord
from discord.ext import commands



class Challenges(commands.Cog):
    EMOJI_YES = '\U00002705' # white check mark on green
    EMOJI_NO = '\U0000274C' # red x
    COLOR_DEF = discord.Colour.from_rgb(0, 191, 0) # red
    COLOR_CULT = discord.Colour.from_rgb(255, 0, 191) # hot pink
    PATH_BASE = Path(__file__).parent
    PATH_DATA = PATH_BASE.parent
    PATH_USERS = PATH_DATA / 'data/users.json'
    PATH_AUTHORS = PATH_DATA / 'data/authors.json'
    PATH_CHALLENGES = PATH_DATA / 'data/tasks_12_2019.json'

    # CHAN_ID_PROOF =(488712787107774495  #HoC|#shameless_self_promotion
    CHAN_ID_PROOF = 651594746891862044    #HoC_Bot_Dev | #images

    def __init__(self, bot):
        self.bot = bot
        self.debug_mode = False

        self.user_data = self.read_json(self.PATH_USERS)
        self.author_data = self.read_json(self.PATH_AUTHORS)
        self.authors = self.author_data.get('authors')

        self._init_challenges()


    @staticmethod
    def read_json(filename):
        with filename.open() as f:
            user_data = json.load(f)
        return user_data


    @staticmethod
    def write_json(data, filename):
        with filename.open(mode='w') as f:
            json.dump(data, f, sort_keys=True, indent=4)
        return f


    def _init_challenges(self):
        self.challenges = self.read_json(self.PATH_CHALLENGES)

        self.title = self.challenges.get('title', 'MistressSyn Challenges')
        self.host = self.challenges.get("host", 'House of Chastity')
        self.year = self.challenges.get('year', 2019)
        self.subtitle = self.challenges.get('subtitle', 'Daily Challenge')
        self.emoji = self.challenges.get('emoji', 'lock')
        self.thumbnail = self.challenges.get('thumbnail')
        self.desc = self.challenges.get('description', 'Enter description')

        self.tasks = self.challenges.get('tasks')


   #  @commands.Cog.listener()
   #  def on_guild_join(self, guild):
   #      """
   #      This event receives the the guild when the bot joins.
   #      """
   #      print(f'Joined {guild.name} with {guild.member_count} users!')


    def _msg_not_registered(self, user):
        """ Message string to let user know they need to register
        
        Arguments:
            user {str} -- user name or @mention
        
        Returns:
            str -- formatted string to send
        """
        return f"{user}, you need to !register before you receive a challenge."


    def _msg_has_challenge(self, user):
        """ Message string to let user know they already have a challenge
        
        Arguments:
            user {str} -- user name or @mention
        
        Returns:
            str -- formatted string to send
        """
        return f"{user}, you already have a challenge assigned. You will need to !complete it before you can receive a new one."


    async def _verify_proof(self, msg):
        author = msg.author
        query = await msg.channel.send(f"{msg.author.mention}, Is this an image or video?")
        await query.add_reaction(self.EMOJI_YES)
        await query.add_reaction(self.EMOJI_NO)


    # @commands.Cog.listener()
    # async def on_message(self, msg):
    #     if msg.author.bot:
    #         return

    #     # if a message with attachments is posted in 'proof' channels, then
    #     # ask the user if it is proof of a completed challenge they have
    #     # active
    #     if msg.channel.id == self.CHAN_ID_PROOF and msg.attachments:
    #         await self._verify_proof(msg)

    #     # print(msg.channel.id)
    #     # if not ctx.message.channel.id == self.CHAN_ID_PROOF:
    #     #     return None
    #     # content = msg.content
    #     # attachments = msg.attachments
    #     # embeds = msg.embeds

    #     # print(f"content : {content}")
    #     # # [<discord.message.Attachment object at 0x000001AE92B18D48>]
    #     # print(f"attachments : {attachments}")
    #     # print(f"embeds : {embeds}")

    #     # await msg.channel.send(f"```{msg.content}```")

    def _is_admin(self, ctx):
        return ctx.message.author.permissions_in(ctx.channel).administrator


    def _output_user_data(self):
        try:
            self.write_json(self.user_data, self.PATH_USERS)
        except:
            print('Failed writing user data to .json!')
            print(self.user_data)


    def _add_user(self, user):
        user_id = str(user.id)
        def_user = {
            'name' : user.name,
            'discriminator' : user.discriminator,
            'nick' : user.nick,
            'cur_challenge' : None,
            'points' : 0
        }
        self.user_data[user_id] = def_user
        self._output_user_data()


    def _del_user(self, user):
        user_id = str(user.id)
        del self.user_data[user_id]
        self._output_user_data()


    # @commands.command()
    # async def debug(self, ctx, state):
    #     """
    #     Turns on debug mode

    #     Arguments:
    #         state {str} -- "true" or "on" to turn debug mode on. "false" or "off" to turn it off.
    #     """
    #     self.debug_mode = state.lower() == "true" or state.lower() == "on"
    #     if self.debug_mode:
    #         await ctx.send(f"Debug mode is on.")
    #     else:
    #         await ctx.send(f"Debug mode is off.")


    # @commands.command()
    # async def show_attrs(self, ctx):
    #     attrs = vars(self)
    #     for k, v in attrs.items():
    #         await ctx.send(f"{k} : {v}")


    # @commands.command(aliases=['get'])
    # async def get_attr(self, ctx, attr):
    #     """
    #     Debug commmand to get an attribute from the bot object
    #     """
    #     attrs = vars(self)
    #     if attr in attrs.keys():
    #         await ctx.send(f"{attr} : {attrs[attr]}")


    @commands.command()
    async def register(self, ctx):
        """
        Register your discord account with SynBot
        """
        user = ctx.message.author
        if str(user.id) in self.user_data.keys():
            await ctx.send(f'{ctx.author.mention}, you are already registered')
            return False

        self._add_user(user)
        await ctx.send('Registered!')


    # @commands.command()
    # async def deregister(self, ctx):
    #     """
    #     Deregisters a discord user with the bot
    #     """
    #     user = ctx.message.author
    #     if not str(user.id) in self.user_data.keys():
    #         await ctx.send('You are not registerd yet!')
    #         return False

    #     self._del_user(user)
    #     await ctx.send('De-registered!')


    def _set_user_challenge(self, user_id, challenge):
        if challenge:
            self.user_data[user_id]['cur_challenge'] = challenge.get('title')
            self._output_user_data()
        else:
            self.user_data[user_id]['cur_challenge'] = None


    def _rand_int(self, match):
        """
        Generates a random integer from re.sub match object

        Arguments:
            match {[type]} -- [description]

        Returns:
            str -- String to replace
        """
        _min, _max = match.group(1, 2)
        rand_int = random.randint(int(_min), int(_max))
        return str(rand_int)


    def _parse_challenge_desc(self, challenge):
        """
        parses description for special formatted functions
        """
        desc = challenge.get('description')
        desc = re.sub("{(\d+)-(\d+)}", self._rand_int, desc)
        return desc


    def _show_challenge(self, ctx, idx, challenge, user=None):
        """
        Creates message/embed bundle for a challenge
        """
        msg = ""
        title = challenge.get('title')
        emoji = challenge.get('emoji')
        if emoji:
            title = f":{emoji}: - #{idx + 1} {title} - :{emoji}:"

        desc = self._parse_challenge_desc(challenge)

        color = self.COLOR_CULT if challenge.get('cult', False) else self.COLOR_DEF
        embed = discord.Embed(title=title, description=desc, color=color)

        if user:
            embed.add_field(name="Assigned To:", value='{}'.format(ctx.author.mention), inline=False)

        thumbnail = challenge.get('thumbnail', self.thumbnail)
        embed.set_thumbnail(url=thumbnail)

        image = challenge.get('image', None)
        if image:
            embed.set_image(url=image)

        links = challenge.get('links', None)
        if links:
            if type(links) is list:
                embed.add_field(name=f"Links:", value='\n'.join(links), inline=False)
            else:
                embed.add_field(name=f"Link:", value=links, inline=False)

        # get author and collect data from authors dataset
        author = challenge.get('author')
        author_data = self.authors.get(author)
        author_name = author_data.get('name')
        author_id = author_data.get('id')
        author_icon = author_data.get('icon')
        # if author_icon:
        #     embed.set_author(name=author_name, icon_url=author_icon)
        # else:
        #     embed.set_author(name=author_name)

        reward = challenge.get('reward', None)
        if reward:
            embed.add_field(name="Reward:", value=reward, inline=False)

        embed.set_footer(text=f"© {self.year} {author_name} - Permissions granted to {self.host}. All rights reserved.")

        return msg, embed


    @commands.command(aliases=['c'])
    async def challenge(self, ctx, idx=None):
        """
        Request a random challenge from SynBot
        """      
        user_id = str(ctx.message.author.id)
        if not user_id in self.user_data.keys() and not self.debug_mode:
            await ctx.send(self._msg_not_registered(ctx.author.mention))
            return False
        if self.user_data[user_id]['cur_challenge'] and not self.debug_mode:
            await ctx.send(self._msg_has_challenge(ctx.author.mention))
            return False

        # challenge = random.choice(self.tasks)
        if idx and self._is_admin(ctx):
            try:
                idx = int(idx) - 1
            except ValueError:
                idx = random.randint(0, len(self.tasks))
        else:
            idx = random.randint(0, len(self.tasks))
        challenge = self.tasks[idx]

        self._set_user_challenge(user_id, challenge)

        msg, embed = self._show_challenge(ctx, idx, challenge, user=ctx.message.author)
        await ctx.channel.send(msg, embed=embed)


    # @commands.command(aliases=['p'])
    # async def punish(self, ctx):
    #     """
    #     Request a random punishment
    #     """
    #     await ctx.channel.send(f"{ctx.author.mention} must be punished!")


    # @commands.command(aliases=['r'])
    # async def reward(self, ctx):
    #     """
    #     Request a random reward
    #     """
    #     await ctx.channel.send(f"{ctx.author.mention} will be rewarded!")


    def _get_points(self, user_id):
        points = self.user_data[user_id].get('points')
        return points


    def _set_points(self, user_id, points):
        self.user_data[user_id]['points'] = points
        self._output_user_data()
        return points


    def _mod_points(self, user_id, points):
        cur_points = self._get_points(user_id)
        points += cur_points
        self._set_points(user_id, points)
        return points


    @commands.command(aliases=['score'])
    async def points(self, ctx):
        """
        Shows the points you have earned from complete challenges
        """
        user_id = str(ctx.message.author.id)
        if not user_id in self.user_data.keys():
            await ctx.send(self._msg_not_registered(ctx.author.mention))
            return False
        points = self._get_points(user_id)
        await ctx.channel.send(f"{ctx.author.mention}, you have {points} point(s).")


    @commands.command()
    async def complete(self, ctx):
        """
        Complete an assigned challenge
        """
        user_id = str(ctx.message.author.id)
        if not user_id in self.user_data.keys():
            await ctx.send(self._msg_not_registered(ctx.author.mention))
            return False
        if not self.user_data[user_id]['cur_challenge']:
            await ctx.send(f"{ctx.author.mention}, you don't have a !challenge assigned.")
            return False

        self._set_user_challenge(user_id, None)

        # ToDo: The number of points awarded should come from the challenge data
        # and other conditions, such as photo/video proof submitted
        points = 1 
        self._mod_points(user_id, points)
        await ctx.channel.send(f"{ctx.author.mention}, you have completed your challenge and gained {points} point(s)!")


    # @commands.command()
    # async def users(self, ctx):
    #     """
    #     Debug command to show registered users
    #     """
    #     print(self.user_data)



def setup(bot):
    bot.add_cog(Challenges(bot))
