# Discord Bot for TGDPSJ Levels

Этот бот позволяет добавлять демонов, челленджи и игроков в репозиторий через команды в Discord.

## Настройка

1. Установите зависимости: `pip install discord.py pygithub python-dotenv`

2. Заполните .env файл: 
   ```
   DISCORD_TOKEN=ваш_дискорд_токен
   GITHUB_TOKEN=ваш_гитхаб_пат
   ```

3. Для локального запуска: `python main.py`

## Хостинг (Railway)

1. Создайте новый репозиторий на GitHub, загрузите файлы бота (.gitignore скроет .env).

2. Аккаунт на railway.app, New Project > Deploy from GitHub repo > Выберите репо.

3. В Variables добавьте DISCORD_TOKEN и GITHUB_TOKEN с их значениями.

## Команды

### Slash commands ( / ) - автодополнение параметров

- `/add_demon` - параметры: name, levelid, creator, imageurl, verifier, xp, [videourl, verifurl]

- `/add_challenge` - аналогично /add_demon

- `/add_player` - параметры: name, avatar, [isadmin=0, levels (level1:url1;level2:url2)]

### Текстовые команды (!)

- `!add_demon [параметры]` - добавить демона

- `!add_challenge [параметры]` - добавить челлендж

- `!add_player [параметры]` - добавить игрока

Формат параметров: ключ:значение разделены пробелами.

Пример: `!add_demon name:Test levelID:123 creator:Me imageURL:img.png Verifier:You xp:100`

Для slash команд права настраиваются в настройках сервера: Server Settings > Integrations > Bot > Permissions For Commands. Выберите роли/пользователей для каждой команды.
