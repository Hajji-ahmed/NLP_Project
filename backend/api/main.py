import os
import time
import logging
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from api.llm_engine import LLMEngine
from api.security import SecurityEngine

# --- 1. LOGGING SETUP ---
# We use abspath to ensure logs go to the right place regardless of where you run the command
LOG_DIR = os.path.abspath("logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure logging to save ALL info to the file
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "requests.log"),
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = FastAPI(title="Secure LLM API (Full Defense)")

# --- 2. CONFIGURATION ---
# Hardcoded Key for Workshop Stability
API_KEY = "groupe3-secret-key-123"

MAIN_MODEL_FILE = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
GUARD_MODEL_FILE = "llama-guard-3-1b-q4_k_m.gguf" 

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Global Variables
llm_engine = None
security_engine = None

# --- 3. STARTUP EVENT ---
@app.on_event("startup")
async def startup_event():
    global llm_engine, security_engine
    print(f" Starting Server...")
    print(f" Logs will be saved to: {os.path.join(LOG_DIR, 'requests.log')}")
    
    try:
        security_engine = SecurityEngine(GUARD_MODEL_FILE)
        llm_engine = LLMEngine(MAIN_MODEL_FILE)
        print(" Startup Complete: All models loaded.")
    except Exception as e:
        print(f" CRITICAL ERROR during startup: {e}")

# --- 4. SECURITY CHECK (With Debugging) ---
async def get_api_key(api_key_token: str = Security(api_key_header)):
    """Verifies the API Key and logs any failures."""
    
    if api_key_token == API_KEY:
        return api_key_token
    else:
        #  DEBUG: Print this to the terminal to see what key was sent
        print(f"\n DEBUG: Access Denied!")
        print(f"   Expected Key: '{API_KEY}'")
        print(f"   Received Key: '{api_key_token}'") # <-- Check this value in your terminal!
        
        logging.warning(f" AUTH FAILED: Invalid Key. Received: '{api_key_token}'")
        raise HTTPException(status_code=403, detail=" Access Denied: Invalid API Key")

# --- 5. DATA MODEL ---
class PromptRequest(BaseModel):
    text: str
    max_new_tokens: int = 128
    temperature: float = 0.7

# --- 6. GENERATION ENDPOINT ---
@app.post("/generate", dependencies=[Depends(get_api_key)])
async def generate(data: PromptRequest):
    start = time.time()
    user_input = data.text
    
    # Log that a request started
    logging.info(f" REQUEST: '{user_input[:30]}...' (Length: {len(user_input)})")

    # Layer 1: Regex
    safe, msg = security_engine.check_layer_1_regex(user_input)
    if not safe:
        logging.warning(f" BLOCKED [Layer 1 Regex]: {msg}")
        return {"response": f" {msg}", "blocked": True}

    # Layer 1.5: Injection
    safe, msg = security_engine.check_layer_1_5_injection(user_input)
    if not safe:
        logging.warning(f" BLOCKED [Layer 1.5 Injection]: {msg}")
        return {"response": f" {msg}", "blocked": True}

    # Layer 2: Llama Guard
    safe, msg = security_engine.check_layer_2_guard(user_input)
    if not safe:
        logging.warning(f" BLOCKED [Layer 2 Guard]: {msg}")
        return {"response": f" {msg}", "blocked": True}

    # Layer 3: XML Escaping
    secure_prompt = security_engine.layer_3_escape(user_input)

    # Construct System Prompt
    final_prompt = f"""You are a helpful AI assistant.
User input data:
{secure_prompt}
Respond safely to the user."""

    # Generate Response
    try:
        response_text = llm_engine.generate(
            prompt=final_prompt, 
            max_tokens=data.max_new_tokens,
            temp=data.temperature
        )
    except Exception as e:
        logging.error(f" MODEL ERROR: {e}")
        return {"response": " Internal Model Error", "blocked": False}

    # Output Filtering
    if hasattr(security_engine, 'check_output'):
        safe_out, msg_out = security_engine.check_output(response_text, user_input)
        if not safe_out:
            logging.warning(f"🛡️ BLOCKED [Output Filter]: {msg_out}")
            return {
                "response": "⛔ Output Blocked: Safety violation.", 
                "latency": time.time()-start, 
                "blocked": True
            }

    # === ✅ SUCCESS ===
    latency = time.time() - start
    logging.info(f"✅ SUCCESS: Latency {latency:.2f}s | Response: '{response_text[:30]}...'")
    
    return {
        "response": response_text,
        "latency": latency,
        "blocked": False
    }