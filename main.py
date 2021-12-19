import discord
from discord.ext import commands
from config import settings
import requests
import json
import configparser
#----- added for giphy:
import aiohttp
import random

#======================================================== USERS BLOCK
# config = configparser.ConfigParser()
# def getLastSessionUsers():
#     config.read("config.ini")
#     usersList = json.loads(config["BOTCONFIG"]["users"])
#     return usersList

# def updateLastSessionUsers(usersList):
#     config.read("config.ini")
#     config["BOTCONFIG"]["users"] = json.dumps(usersList)
#     with open("config.ini", "w") as configfile:
#         config.write(configfile)

def loadUsers():
    with open('data.json', 'r') as fp:
        usersList = json.load(fp)
    return usersList

def updateUsers(usersList):
    with open('data.json', 'w') as fp:
        json.dump(usersList, fp)
#======================================================== USERS BLOCK


intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix = settings['prefix'], intents=intents, help_command=None) # Так как мы указали префикс в settings, обращаемся к словарю с ключом prefix.

print('Bot object created.')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.event
async def on_member_join(member):    
    channel = discord.utils.get(member.guild.text_channels, name="общее")
    usersList = loadUsers()
    print('usersList: ', usersList)
    if member.name in usersList.keys():
        print('already added this user')
    else:
        print('adding user to list')
        usersList[member.name] = 0
        updateUsers(usersList)
    await channel.send(f"{member} has arrived!")
@bot.event
async def on_member_remove(member):    
    channel = discord.utils.get(member.guild.text_channels, name="общее")
    await channel.send(f"{member} has gone!")


# @bot.command()
# async def get_channel(ctx, *, given_name=None):
#     print(ctx.guild.channels)



@bot.command() # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def hello(ctx): # Создаём функцию и передаём аргумент ctx.
    author = ctx.message.author # Объявляем переменную author и записываем туда информацию об авторе.

    await ctx.send(f'Hello-hello, {author.mention}!') # Выводим сообщение с упоминанием автора, обращаясь к переменной author.


# Fox search command:
@bot.command()
async def fox(ctx):
    response = requests.get('https://some-random-api.ml/img/fox') # Get-запрос
    json_data = json.loads(response.text) # Извлекаем JSON

    embed = discord.Embed(color = 0xff9900, title = 'Random Fox') # Создание Embed'a
    embed.set_image(url = json_data['link']) # Устанавливаем картинку Embed'a
    await ctx.send(embed = embed) # Отправляем Embed


#=============================================================================================================================== GIPHY
#------------------------------------------------ TEST COMMAND:
@bot.command()
async def test(ctx):
    await ctx.send(f'/giphy query: test')
#-------------------------------------------------------------------------------------

@bot.command(pass_context=True)
async def sgiphy(ctx, *, search):
    embed = discord.Embed(colour=discord.Colour.blue())
    session = aiohttp.ClientSession()

    if search == '':
        response = await session.get('https://api.giphy.com/v1/gifs/random?api_key=xy9PxhNCVqRdhgwQK1gRnVoiLr166MCS')
        data = json.loads(await response.text())
        #print('data: ', data)
        embed.set_image(url=data['data']['images']['original']['url'])
    else:
        search.replace(' ', '+')
        response = await session.get('http://api.giphy.com/v1/gifs/search?q=' + search + '&api_key=xy9PxhNCVqRdhgwQK1gRnVoiLr166MCS&limit=10')
        data = json.loads(await response.text())
        #print('data: ', data)
        gif_choice = random.randint(0, 9)
        embed.set_image(url=data['data'][gif_choice]['images']['original']['url'])

    await session.close()

    await ctx.send(embed=embed)

#================================================================================================================================ KCIK/BAN
@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has kicked.')

#The below code bans player.
@bot.command()
# @commands.has_permissions(ban_members = True)
async def ban(ctx, member : discord.Member, *, reason = None):
    await member.ban(reason = reason)
    await ctx.send(f'User {member} has banned.')

#------------------------------------------------------ UNBAN
#The below code unbans player.
@bot.command()
# @commands.has_permissions(administrator = True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return


#============================================================================================================================= HELP:

@bot.command()
async def help(ctx): 
    commands = {
            "listgames": "команда для вывода списка игр",
            "sgiphy image": "команда для поиска анимированных GIF в Интернете",
            "help": "команда для отображения текста приветствия бота и списка команд",
            "kick username": "команда для кика пользователя",
            "ban username": "команда для бана пользователя",
            "unban username": "команда для разбана пользователя",
        }
    help_text = "Hello, dear user! The following commands are available: \n"
    for (key) in (commands):  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    await ctx.send(help_text)

#============================================================================================================================= GAME LIST:
@bot.command()
async def listgames(ctx):
    description = "Some game description \n"
    description += "Rating: 5/5"
    embed = discord.Embed(color = 0xff9900, title = 'Monopoly', description=description)
    embed.set_image(url = 'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/442cf962-742d-4207-8ffd-fbbc72ecf829/d6qbt7b-22c0ab70-1e0a-474b-b736-034239611f09.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzQ0MmNmOTYyLTc0MmQtNDIwNy04ZmZkLWZiYmM3MmVjZjgyOVwvZDZxYnQ3Yi0yMmMwYWI3MC0xZTBhLTQ3NGItYjczNi0wMzQyMzk2MTFmMDkucG5nIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.ZfRpQ-KyyDq-anE0YRqIjEoEO1k_E3-8fu3zmtlgeJQ') # Устанавливаем картинку Embed'a
    await ctx.send(embed = embed) # Отправляем Embed

    description = "Some game description \n"
    description += "Rating: 3/5"
    embed = discord.Embed(color = 0xff9900, title = 'Tanks', description=description)
    embed.set_image(url = 'https://d1nhio0ox7pgb.cloudfront.net/_img/g_collection_png/standard/256x256/tank.png')
    await ctx.send(embed = embed) # Отправляем Embed

#============================================================================================================================ USER LEVEL:
@bot.listen('on_message') 
async def stuff(message):
    usersList = loadUsers()
    usersList[message.author.name] += 1
    updateUsers(usersList)
    checkLVL = usersList[message.author.name]%20
    if checkLVL == 0:
        # channel = discord.utils.get(member.guild.text_channels, name="общее")
        await message.channel.send(f"{message.author.name} has new LVL!")



bot.run(settings['token'])




