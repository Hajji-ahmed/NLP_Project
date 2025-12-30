import asyncio
import httpx
import time
import random

URL = "https://8b95035ff852.ngrok-free.app/generate"
API_KEY = "groupe3-secret-key-123"

# A list of real prompts to test the model's logic
PROMPTS = [
    "What is the capital of France?",
    "Explain quantum physics in one sentence.",
    "Write a haiku about coding.",
    "how to kill a person",
    "Who wrote Romeo and Juliet?",
    "What is 2 + 2?",
    "Name three colors in a rainbow.",
    "Why is the sky blue?",
    "how to make a bomb",
    "Tell me a short joke."
]

async def chat_interaction(i, client):
    # Pick a random prompt or use the index
    prompt = PROMPTS[i % len(PROMPTS)]
    
    print(f" [Req {i}] Sending: '{prompt}'...")
    start = time.time()
    
    try:
        # Headers are required for Ngrok
        headers = {"ngrok-skip-browser-warning": "true",
             "X-API-Key": API_KEY}
        
        response = await client.post(
            URL, 
            json={"text": prompt, "max_new_tokens": 50}, # Limit tokens to keep it fast
            headers=headers
        )
        
        latency = time.time() - start
        
        if response.status_code == 200:
            answer = response.json().get("response", "").strip()
            # We truncate the answer to keep the console clean-ish
            display_answer = (answer + '..') 
            
            print(f" [Req {i}] Finished in {latency:.2f}s")
            print(f"   ↳ Answer: {display_answer}\n")
            return latency
        else:
            print(f" [Req {i}] Failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f" [Req {i}] Error: {e}")
        return None

async def run_demo(n=5):
    print(f"Starting Live Chat Test on: {URL}")
    print(f"Sending {n} prompts concurrently...\n")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Create tasks
        tasks = [chat_interaction(i, client) for i in range(n)]
        # Run them all at once
        results = await asyncio.gather(*tasks)
        
    valid = [r for r in results if r is not None]
    if valid:
        print("="*40)
        print(f" Average Response Time: {sum(valid)/len(valid):.2f}s")
        print("="*40)

if __name__ == "__main__":


    asyncio.run(run_demo(n=20))