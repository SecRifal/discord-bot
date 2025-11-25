# Discord Bot for TGDPSJ Impossible Levels

Этот бот позволяет добавлять impossible levels в репозиторий через команду в Discord.

## Настройка

1. Установите зависимости: `pip install discord.py pygithub python-dotenv requests`

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

- `/ill_add` - добавить impossible level
  Параметры:
  - position: int (позиция уровня)
  - name: str (название)
  - level_id: str (ID уровня)
  - creator: str (создатель)
  - video_url: str (ссылка на видео, опционально)
  - img: файл (прикрепить изображение)

Для slash команд права настраиваются в настройках сервера: Server Settings > Integrations > Bot > Permissions For Commands. Выберите роли/пользователей для команды.
