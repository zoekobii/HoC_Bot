import asyncio
import datetime
import json
import logging
import os
from pathlib import Path

import discord
from discord.ext import commands



BASE_PATH = Path(__file__).parent


def config_load():
    filename = BASE_PATH / r"data/config.json" 
    with open(filename, 'r', encoding='utf-8') as doc:
        #  Please make sure encoding is correct, especially after editing the config file
        return json.load(doc)


async def run():
    """
    Where the bot gets started. If you wanted to create an database connection
    pool or other session for the bot to use, it's recommended that you create
    it here and pass it to the bot as a kwarg.
    """

    config = config_load()
    bot = Bot(config=config, description=config['description'])
    try:
        await bot.start(config['token'])
    except KeyboardInterrupt:
        await bot.logout()



class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=self.get_prefix_,
            description=kwargs.pop('description')
        )
        self.start_time = None
        self.app_info = None

        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())

        logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(message)s')


    async def track_start(self):
        """
        Waits for the bot to connect to discord and then records the time.
        Can be used to work out uptime.
        """
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()


    async def get_prefix_(self, bot, message):
        """
        A coroutine that returns a prefix.

        I have made this a coroutine just to show that it can be done. If you needed async logic in here it can be done.
        A good example of async logic would be retrieving a prefix from a database.
        """
        prefix = ['!']
        return commands.when_mentioned_or(*prefix)(bot, message)


    async def load_all_extensions(self):
        """
        Attempts to load all .py files in /cogs/ as cog extensions
        """
        await self.wait_until_ready()
        await asyncio.sleep(1)  # ensure that on_ready has completed and finished printing
        cog_scripts = (BASE_PATH / r"cogs").glob('*.py')
        cogs = [x.stem for x in cog_scripts ]
        for extension in cogs:
            try:
                self.load_extension(f'cogs.{extension}')
                print(f'loaded {extension}')
            except Exception as e:
                error = f'{extension}\n {type(e).__name__} : {e}'
                print(f'failed to load extension {error}')
            print('-' * 10)


    async def on_ready(self):
        """
        This event is called every time the bot connects or resumes connection.
        """
        print('-' * 10)
        self.app_info = await self.application_info()
        print(f'Logged in as: {self.user.name}\n'
              f'Using discord.py version: {discord.__version__}\n'
              f'Owner: {self.app_info.owner}\n'
              f'Template Maker: SourSpoon / Spoon#7805')
        print('-' * 10)


    async def on_message(self, message):
        """
        This event triggers on every message received by the bot. Including one's that it sent itself.

        If you wish to have multiple event listeners they can be added in other cogs. All on_message listeners should
        always ignore bots.
        """
        if message.author.bot:
            return  # ignore all bots
        await self.process_commands(message)



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
