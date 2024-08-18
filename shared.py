from flask import Flask, Blueprint
from flask_cors import CORS
import discord
import os
from modules.utils.db import DBConnect


import asyncio
from modules.utils.config import Config
# from modules.utils.db import DBManager

from modules.utils.db import DBConnect, Base
from modules.utils.TokenManager import TokenManager
from modules.bot.discord_modules.bot import BotFork

from modules.users.invite import ClubInvitationSender

username = input("Enter your ASU ID:")
password = input("Enter your ASU password:")

config = Config()
app = Flask ("SoDA internal API", static_folder=None, template_folder=None)


# Initialize database connection
db_connect = DBConnect('sqlite:///./user.db')  # Adjust the URL to your database
app = Flask("SoDA internal API", static_folder=None, template_folder=None)
CORS(app)
tokenManger = TokenManager()

invite = ClubInvitationSender(username=username, password=password, invitation_url='https://asu.campuslabs.com/engage/actioncenter/organization/soda/roster/Roster/invite')
