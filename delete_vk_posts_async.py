import asyncio
import aiohttp
import time

# =====================================
#            НАСТРОЙКИ
# =====================================
ACCESS_TOKEN    = 'vk1.a.ВАШ_ТОКЕН_ЗДЕСЬ'  # User access token с правами wall, groups
GROUP_ID        = -123456789               # Отрицательный ID вашего сообщества
API_VERSION     = '5.131'                  # Версия VK API
BATCH_SIZE      = 100                      # Сколько постов за раз запрашивать
MAX_CONCURRENT  = 3                        # Сколько одновременных delete-запросов
DELAY           = 0.3                      # Пауза (в секундах) после каждого удаления
# =====================================

async def fetch_posts(session: aiohttp.ClientSession) -> list:
    """
    Запрашивает у VK до BATCH_SIZE последних постов, опубликованных от имени группы.

    :param session: aiohttp.ClientSession для выполнения HTTP-запросов
    :return: список объектов постов (dict), если постов нет — пустой список
    :raises RuntimeError: при ошибке API (ключ "error" в ответе)
    """
    params = {
        'access_token': ACCESS_TOKEN,
        'v':            API_VERSION,
        'owner_id':     GROUP_ID,
        'count':        BATCH_SIZE,
        'filter':       'owner'  # Только посты, созданные сообществом
    }
    async with session.get('https://api.vk.com/method/wall.get', params=params) as resp:
        data = await resp.json()
        if 'error' in data:
            # Если VK вернул ошибку, прерываем выполнение
            raise RuntimeError(f"Ошибка wall.get: {data['error']['error_msg']}")
        items = data['response']['items']
        print(f"🔍 Осталось для удаления: {len(items)}")
        return items

def make_delete_post(semaphore: asyncio.Semaphore):
    """
    Фабрика функций удаления поста с учётом ограничения по параллелизму.

    :param semaphore: asyncio.Semaphore для ограничения числа одновременных задач
    :return: coroutine-функция delete_post(session, post_id)
    """
    async def delete_post(session: aiohttp.ClientSession, post_id: int) -> None:
        """
        Удаляет один пост по его ID.

        :param session: aiohttp.ClientSession для HTTP-запросов
        :param post_id: числовой ID поста в группе
        """
        async with semaphore:
            params = {
                'access_token': ACCESS_TOKEN,
                'v':            API_VERSION,
                'owner_id':     GROUP_ID,
                'post_id':      post_id
            }
            # Выполнение запроса на удаление поста
            async with session.post('https://api.vk.com/method/wall.delete', params=params) as resp:
                result = await resp.json()
                if 'error' in result:
                    # Выводим сообщение об ошибке удаления
                    print(f"❌ Пост {post_id}: {result['error']['error_msg']}")
                else:
                    print(f"✅ Удалён пост {post_id}")
            # Задержка, чтобы не превысить rate limit
            await asyncio.sleep(DELAY)

    return delete_post

async def main() -> None:
    """
    Основная корутина:
    - Заводит таймер.
    - Циклически запрашивает и удаляет посты пачками.
    - Подсчитывает и выводит общее число удалённых постов и затраченное время.
    """
    # Запуск таймера
    start_time = time.perf_counter()
    total_deleted = 0

    # Создаём Semaphore внутри активного event loop
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    delete_post = make_delete_post(semaphore)

    # Открываем HTTP-сессию для всех запросов
    async with aiohttp.ClientSession() as session:
        while True:
            # Получаем следующую пачку
            posts = await fetch_posts(session)
            if not posts:
                # Если больше нет постов — выходим из цикла
                break

            # Стартуем удаление каждого поста в пачке
            tasks = [asyncio.create_task(delete_post(session, p['id'])) for p in posts]
            # Дожидаемся завершения всех задач в этой пачке
            await asyncio.gather(*tasks)

            total_deleted += len(posts)

    # Останавливаем таймер и форматируем время
    elapsed = time.perf_counter() - start_time
    hrs, rem = divmod(elapsed, 3600)
    mins, secs = divmod(rem, 60)

    # Итоговый вывод
    print(f"\n🎉 Готово! Всего удалено постов: {total_deleted}")
    print(f"⏱ Затрачено времени: {int(hrs):02}:{int(mins):02}:{secs:05.2f}")

if __name__ == '__main__':
    asyncio.run(main())
