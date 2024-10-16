import time
import asyncio
import aiohttp

# URL вашего приложения
BASE_URL = "http://localhost:8080"

async def send_request(session, url):
    try:
        async with session.get(url) as response:
            status = response.status
            data = await response.json()
            print(f"Status: {status}, Response: {data}")
    except Exception as e:
        print(f"Request failed: {e}")

async def send_requests():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(10):  # Отправляем 10 запросов одновременно
            url = f"{BASE_URL}/cart"
            tasks.append(send_request(session, url))


        await asyncio.gather(*tasks)

def main():
    while True:
        asyncio.run(send_requests())
        time.sleep(1)

if __name__ == "__main__":
    main()
