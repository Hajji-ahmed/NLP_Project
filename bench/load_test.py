import asyncio, httpx, time

URL = "http://localhost:8000/generate"

async def call(i, client):
    start = time.time()
    r = await client.post(URL, json={"text": f"Test {i}", "max_new_tokens": 20})
    latency = time.time() - start
    return latency

async def run(n=50):
    async with httpx.AsyncClient(timeout=60.0) as client:
        tasks = [call(i, client) for i in range(n)]
        results = await asyncio.gather(*tasks)
        print("Moyenne latence:", sum(results) / len(results))

if __name__ == "__main__":
    asyncio.run(run(20))  # Réduit de 100 à 20 requêtes simultanées
