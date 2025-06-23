# VK Group Post Cleaner

«VK Group Post Cleaner» содержит готовый к использованию асинхронный Python-скрипт для массового удаления всех постов, опубликованных от имени вашего сообщества ВКонтакте. Скрипт построен на asyncio + aiohttp, автоматически запрашивает последние публикации пачками, удаляет их с контролем параллелизма и задержкой для обхода rate-limit’а API и выводит подробную статистику по удалённым записям и затраченному времени.

## 🚀 Быстрый старт

1. Клонировать репозиторий:
   ```bash
   git clone https://github.com/ypnikotin/vk_group_post_cleaner.git
   cd название_репо

2. Создать виртуальное окружение и установить зависимости:
   ```bash
    python3 -m venv .venv
    source .venv/bin/activate         # Linux / macOS
    .venv\Scripts\activate            # Windows
    pip install -r requirements.txt
    ```
    
3. Вставить ваш VK user access token в ```delete_vk_posts_async.py```.
- Токен должен иметь права: ```wall```, ```groups```, ```offline```.
- ```GROUP_ID``` — отрицательный ID вашего сообщества (например, -123456789).

4. Запустить скрипт:
  ```bash
  python delete_vk_posts_async.py
  ```

## ⚙️ Конфигурация


В начале delete_vk_posts_async.py доступны настройки:

### Jписание
- **ACCESS_TOKEN** - Ваш user access token VK
- **GROUP_ID** - Отрицательный ID сообщества (с минусом)
- **BATCH_SIZE** - Сколько постов запрашивать за раз (макс. 100)
- **MAX_CONCURRENT** - Сколько одновременных удалений
- **DELAY** - Пауза (сек.) после каждого запроса на удаление

## 🛠 Troubleshooting

- Ошибка ```method is unavailable with group auth```
→ Используйте user access token администратора сообщества, а не групповой.
- Ошибка ```Too many requests per second```
→ Увеличьте ```DELAY``` или уменьшите ```MAX_CONCURRENT```.
- Капча или другие rate-limit
→ Добавьте более длинную паузу или разбейте удаление на несколько запусков.

