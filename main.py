import discord
from discord import app_commands
from discord.ext import commands
import json
import requests
import os
from github import Github
from github.GithubException import GithubException
# Настройки GitHub
GITHUB_REPO = 'SecRifal/TGDPSJ'
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Проверка наличия токенов
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable is not set.")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is not set.")

# Discord Bot настройки
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await bot.tree.sync()

# Slash command /ill_add
@bot.tree.command(name='ill_add', description='Добавить impossible level')
async def slash_ill_add(ctx: discord.Interaction,
                        position: int,
                        name: str,
                        level_id: str,
                        creator: str,
                        video_url: str = None,
                        img: discord.Attachment = None):
    try:
        await ctx.response.defer()
    except discord.errors.NotFound as e:
        if e.code == 10062:  # Unknown interaction
            return  # Interaction timed out, nothing we can do
        else:
            raise  # Re-raise other NotFound errors

    # Проверка прикрепления img
    if not img:
        await ctx.followup.send("Необходимо прикрепить изображение (img).")
        return

    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)

        # Скачать изображение
        image_data = requests.get(img.url).content

        # Определить расширение файла (сохранить оригинальное)
        ext = img.filename.rsplit('.', 1)[-1] if '.' in img.filename else 'png'

        # Создать имя файла на основе названия уровня, санитизировать
        import re
        sanitized_name = re.sub(r'[^\w\-_\. ]', '_', name).strip().replace(' ', '_')
        image_filename = f"{sanitized_name}.{ext}"

        # Путь для файла: images/impossible/{image_filename}
        image_path = f'images/impossible/{image_filename}'

        # Создаёт папку images/impossible автоматически при загрузке файла
        try:
            repo.create_file(path=image_path, message=f"Upload image for {name}", content=image_data)
            img_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{image_path}"
        except GithubException:
            # Если файл существует, или папка не существует, но create_file создаст с путем
            # Предполагаем, что проходит
            await ctx.followup.send("Ошибка загрузки изображения.")
            return

        data = {
            "position": position,
            "name": name,
            "levelID": level_id,
            "creator": creator,
            "videoURL": video_url or None,
            "img": img_url
        }

        # Получить или создать impossible.json
        filename = 'impossible.json'
        commit_msg = f"Added impossible level {name}"

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

        # Проверка дубликатов
        if any(d.get('levelID') == data['levelID'] for d in current_json):
            await ctx.followup.send("Уровень с таким levelID уже существует.")
            return
        if any(d.get('name') == data['name'] for d in current_json):
            await ctx.followup.send("Уровень с таким именем уже существует.")
            return

        current_json.append(data)

        content = json.dumps(current_json, indent=2, ensure_ascii=False)

        if sha:
            repo.update_file(path=filename, message=commit_msg, content=content, sha=sha)
        else:
            repo.create_file(path=filename, message=commit_msg, content=content)

        await ctx.followup.send(f"Impossible level '{name}' добавлен успешно.")

    except Exception as e:
        await ctx.followup.send(f"Ошибка: {str(e)}")

# Slash command /ill_edit
@bot.tree.command(name='ill_edit', description='Редактировать impossible level')
async def slash_ill_edit(ctx: discord.Interaction,
                        level_id: str,
                        position: int = None,
                        name: str = None,
                        creator: str = None,
                        video_url: str = None,
                        img: discord.Attachment = None):
    try:
        await ctx.response.defer()
    except discord.errors.NotFound as e:
        if e.code == 10062:  # Unknown interaction
            return  # Interaction timed out, nothing we can do
        else:
            raise  # Re-raise other NotFound errors

    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)

        # Получить impossible.json
        filename = 'impossible.json'
        try:
            file_content = repo.get_contents(filename)
            current_json = json.loads(file_content.decoded_content.decode())
            sha = file_content.sha
        except GithubException as e:
            if e.status == 404:
                await ctx.followup.send("Файл impossible.json не найден.")
                return
            else:
                raise

        if not isinstance(current_json, list):
            await ctx.followup.send("Файл не является массивом JSON.")
            return

        # Найти уровень по level_id
        level_index = None
        for i, level in enumerate(current_json):
            if level.get('levelID') == level_id:
                level_index = i
                break

        if level_index is None:
            await ctx.followup.send(f"Уровень с levelID '{level_id}' не найден.")
            return

        level_data = current_json[level_index]
        updated = False

        # Обновить поля если предоставлены
        if position is not None:
            level_data['position'] = position
            updated = True
        if name is not None:
            level_data['name'] = name
            updated = True
        if creator is not None:
            level_data['creator'] = creator
            updated = True
        if video_url is not None:
            level_data['videoURL'] = video_url
            updated = True

        # Если новое изображение, загрузить
        if img:
            # Скачать изображение
            image_data = requests.get(img.url).content

            # Определить расширение файла
            ext = img.filename.rsplit('.', 1)[-1] if '.' in img.filename else 'png'

            # Создать имя файла
            import re
            sanitized_name = re.sub(r'[^\w\-_\. ]', '_', name or level_data['name']).strip().replace(' ', '_')
            image_filename = f"{sanitized_name}.{ext}"

            # Путь для файла
            image_path = f'images/impossible/{image_filename}'

            # Загрузить изображение
            try:
                repo.create_file(path=image_path, message=f"Update image for {name or level_data['name']}", content=image_data)
                img_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{image_path}"
                level_data['img'] = img_url
                updated = True
            except GithubException:
                await ctx.followup.send("Ошибка загрузки нового изображения.")
                return

        if not updated:
            await ctx.followup.send("Нет изменений для сохранения.")
            return

        # Сохранить изменения
        content = json.dumps(current_json, indent=2, ensure_ascii=False)
        commit_msg = f"Updated impossible level {level_id}"
        repo.update_file(path=filename, message=commit_msg, content=content, sha=sha)

        await ctx.followup.send(f"Impossible level '{level_data['name']}' (levelID: {level_id}) обновлен успешно.")

    except Exception as e:
        await ctx.followup.send(f"Ошибка: {str(e)}")

# Slash command /ill_delete
@bot.tree.command(name='ill_delete', description='Удалить impossible level')
async def slash_ill_delete(ctx: discord.Interaction,
                            level_id: str):
    try:
        await ctx.response.defer()
    except discord.errors.NotFound as e:
        if e.code == 10062:  # Unknown interaction
            return  # Interaction timed out, nothing we can do
        else:
            raise  # Re-raise other NotFound errors

    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)

        # Получить impossible.json
        filename = 'impossible.json'
        try:
            file_content = repo.get_contents(filename)
            current_json = json.loads(file_content.decoded_content.decode())
            sha = file_content.sha
        except GithubException as e:
            if e.status == 404:
                await ctx.followup.send("Файл impossible.json не найден.")
                return
            else:
                raise

        if not isinstance(current_json, list):
            await ctx.followup.send("Файл не является массивом JSON.")
            return

        # Найти уровень по level_id
        level_index = None
        for i, level in enumerate(current_json):
            if level.get('levelID') == level_id:
                level_index = i
                break

        if level_index is None:
            await ctx.followup.send(f"Уровень с levelID '{level_id}' не найден.")
            return

        level_data = current_json[level_index]
        level_name = level_data.get('name', 'Unknown')

        # Удалить изображение если существует
        img_path = level_data.get('img')
        if img_path:
            # Получить путь файла из URL
            relative_path = img_path.replace(f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/", "")
            try:
                file_content = repo.get_contents(relative_path)
                repo.delete_file(path=relative_path, message=f"Deleted image for {level_name}", sha=file_content.sha)
            except GithubException as e:
                if e.status != 404:  # Если файл не найден, игнорировать
                    await ctx.followup.send(f"Ошибка удаления изображения: {str(e)}")
                    return

        # Удалить уровень из массива
        current_json.pop(level_index)

        # Сохранить изменения
        content = json.dumps(current_json, indent=2, ensure_ascii=False)
        commit_msg = f"Deleted impossible level {level_id}"
        repo.update_file(path=filename, message=commit_msg, content=content, sha=sha)

        await ctx.followup.send(f"Impossible level '{level_name}' (levelID: {level_id}) удален успешно.")

    except Exception as e:
        await ctx.followup.send(f"Ошибка: {str(e)}")

bot.run(DISCORD_TOKEN)
