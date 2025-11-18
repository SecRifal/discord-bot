import discord
from discord import app_commands
from discord.ext import commands
import json
import requests
import os
from github import Github
from github.GithubException import GithubException
from dotenv import load_dotenv

load_dotenv()

# Настройки GitHub
GITHUB_REPO = 'SecRifal/TGDPSJ'
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Discord Bot настройки
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await bot.tree.sync()

# Slash commands
@bot.tree.command(name='add_demon', description='Добавить демона')
async def slash_add_demon(ctx: discord.Interaction,
                  name: str,
                  levelid: str,
                  creator: str,
                  imageurl: str,
                  verifier: str,
                  xp: int,
                  videourl: str = None,
                  verifurl: str = None):
    data = {
        "name": name,
        "levelID": levelid,
        "creator": creator,
        "videoURL": videourl or False,
        "imageURL": imageurl,
        "Verifier": verifier,
        "verifURL": verifurl or False,
        "xp": xp
    }
    commit_msg = f"Added demon {name}"
    await add_to_repo_slash(ctx, 'demons.json', data, commit_msg)

@bot.tree.command(name='add_challenge', description='Добавить челлендж')
async def slash_add_challenge(ctx: discord.Interaction,
                     name: str,
                     levelid: str,
                     creator: str,
                     imageurl: str,
                     verifier: str,
                     xp: int,
                     videourl: str = None,
                     verifurl: str = None):
    data = {
        "name": name,
        "levelID": levelid,
        "creator": creator,
        "videoURL": videourl or False,
        "imageURL": imageurl,
        "Verifier": verifier,
        "verifURL": verifurl or False,
        "xp": xp
    }
    commit_msg = f"Added challenge {name}"
    await add_to_repo_slash(ctx, 'challenges.json', data, commit_msg)

@bot.tree.command(name='add_player', description='Добавить игрока')
async def slash_add_player(ctx: discord.Interaction,
                   name: str,
                   avatar: str,
                   isadmin: int = 0,
                   levels: str = None):
    completedLevels = []
    if levels:
        for item in levels.split(';'):
            if ':' in item:
                level_name, url = item.split(':', 1)
                completedLevels.append({"name": level_name.strip(), "videoUrl": url.strip()})

    data = {
        "name": name,
        "avatar": avatar,
        "isAdmin": bool(isadmin),
        "completedLevels": completedLevels
    }
    commit_msg = f"Added player {name}"
    await add_to_repo_slash(ctx, 'players.json', data, commit_msg)

async def add_to_repo_slash(ctx, filename, data, commit_msg):
    await ctx.response.defer()
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)

        try:
            file_content = repo.get_contents(filename)
            current_json = json.loads(file_content.decoded_content.decode())
            sha = file_content.sha
        except GithubException as e:
            if e.status == 404:
                current_json = []
                sha = None
            else:
                raise

        if not isinstance(current_json, list):
            await ctx.followup.send("Файл не является массивом JSON.")
            return

        if 'levelID' in data and any(d.get('levelID') == data['levelID'] for d in current_json):
            await ctx.followup.send("Уровень с таким levelID уже существует.")
            return
        elif any(d.get('name') == data['name'] for d in current_json):
            await ctx.followup.send("Объект с таким именем уже существует.")
            return

        current_json.append(data)

        if sha:
            repo.update_file(path=filename, message=commit_msg, content=json.dumps(current_json, indent=2, ensure_ascii=False), sha=sha)
        else:
            repo.create_file(path=filename, message=commit_msg, content=json.dumps(current_json, indent=2, ensure_ascii=False))

        await ctx.followup.send(f"Добавлено успешно в {filename}.")
    except Exception as e:
        await ctx.followup.send(f"Ошибка: {str(e)}")

@bot.command(name='add_demon')
async def add_demon(ctx, *, args):
    # Парсинг аргументов
    params = parse_params(args)
    required = ['name', 'levelID', 'creator', 'imageURL', 'Verifier', 'xp']
    if not all(k in params for k in required):
        await ctx.send("Нужны параметры: name levelID creator imageURL Verifier xp [videoURL verifURL]")
        return

    # Заполнение опциональных
    data = {
        "name": params['name'],
        "levelID": params['levelID'],
        "creator": params['creator'],
        "videoURL": params.get('videoURL', False),
        "imageURL": params['imageURL'],
        "Verifier": params['Verifier'],
        "verifURL": params.get('verifURL', False),
        "xp": int(params['xp'])
    }

    await add_to_repo(ctx, 'demons.json', data, f"Added demon {data['name']}")

@bot.command(name='add_challenge')
async def add_challenge(ctx, *, args):
    params = parse_params(args)
    required = ['name', 'levelID', 'creator', 'imageURL', 'Verifier', 'xp']
    if not all(k in params for k in required):
        await ctx.send("Нужны параметры: name levelID creator imageURL Verifier xp [videoURL verifURL]")
        return

    data = {
        "name": params['name'],
        "levelID": params['levelID'],
        "creator": params['creator'],
        "videoURL": params.get('videoURL', False),
        "imageURL": params['imageURL'],
        "Verifier": params['Verifier'],
        "verifURL": params.get('verifURL', False),
        "xp": int(params['xp'])
    }

    await add_to_repo(ctx, 'challenges.json', data, f"Added challenge {data['name']}")

@bot.command(name='add_player')
async def add_player(ctx, *, args):
    params = parse_params(args)
    required = ['name', 'avatar']
    if not all(k in params for k in required):
        await ctx.send("Нужны параметры: name avatar isAdmin:0or1 [levels:level1:url1;level2:url2]")
        return

    completedLevels = []
    if 'levels' in params:
        for item in params['levels'].split(';'):
            if item.strip():
                level, url = item.split(':', 1)
                completedLevels.append({"name": level.strip(), "videoUrl": url.strip()})

    data = {
        "name": params['name'],
        "avatar": params['avatar'],
        "isAdmin": bool(int(params.get('isAdmin', '0'))),
        "completedLevels": completedLevels
    }

    await add_to_repo(ctx, 'players.json', data, f"Added player {data['name']}")

def parse_params(args):
    params = {}
    for part in args.split():
        if ':' in part:
            key, value = part.split(':', 1)
            params[key] = value
    return params

async def add_to_repo(ctx, filename, data, commit_msg):
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)

        # Получить текущее содержимое файла
        try:
            file_content = repo.get_contents(filename)
            current_json = json.loads(file_content.decoded_content.decode())
            sha = file_content.sha
        except GithubException as e:
            if e.status == 404:
                # Файл не существует, создать с пустым массивом
                current_json = []
                sha = None
            else:
                raise

        # Валидация: проверить тип данных
        if not isinstance(current_json, list):
            await ctx.send("Файл не является массивом JSON.")
            return

        # Добавить новый элемент, если не дублируется (по levelID или name)
        if 'levelID' in data and any(d.get('levelID') == data['levelID'] for d in current_json):
            await ctx.send("Уровень с таким levelID уже существует.")
            return
        elif any(d.get('name') == data['name'] for d in current_json):
            await ctx.send("Объект с таким именем уже существует.")
            return

        current_json.append(data)

        # Обновить файл
        if sha:
            repo.update_file(
                path=filename,
                message=commit_msg,
                content=json.dumps(current_json, indent=2, ensure_ascii=False),
                sha=sha
            )
        else:
            repo.create_file(
                path=filename,
                message=commit_msg,
                content=json.dumps(current_json, indent=2, ensure_ascii=False)
            )

        await ctx.send(f"Добавлено успешно в {filename}.")
    except Exception as e:
        await ctx.send(f"Ошибка: {str(e)}")

bot.run(DISCORD_TOKEN)
