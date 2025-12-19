import os
import time
import logging
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from api.llm_engine import LLMEngine
from api.security import SecurityEngine

# --- 1. LOGS SETUP ---
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/requests.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

app = FastAPI(title="Secure LLM API (Full Defense)")

# --- 2. CONFIGURATION ---
# Models
MAIN_MODEL_FILE = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
# Use the correct generic name if you are switching models often, or keep specific
GUARD_MODEL_FILE = "llama-guard-3-1b-q4_k_m.gguf" 

# 🔐 SECURITY CONFIGURATION (New!)
# We fetch the key from the environment (injected by your Kaggle script)
API_KEY = os.getenv("LLM_API_KEY")

# Safety check: Prevent server from starting if no key is set
if not API_KEY:
    # On Kaggle, this might happen if you forget the 'env=...' line. 
    # We set a default ONLY for debugging if needed, but better to raise error.
    print("⚠️ WARNING: LLM_API_KEY not found! API is unprotected.")
    API_KEY = "default-unsafe-key" 

# Define the header expected: X-API-Key: your-secret
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# --- 3. GLOBAL INSTANCES ---
llm_engine = None
security_engine = None

@app.on_event("startup")
async def startup_event():
    global llm_engine, security_engine
    print("🚀 Starting Server Components...")
    
    # Load Security Engine
    security_engine = SecurityEngine(GUARD_MODEL_FILE)
    
    # Load Main Chat Model
    # If you switched to Qwen 1.5 in the script, ensure this filename matches!
    llm_engine = LLMEngine(MAIN_MODEL_FILE)
    print("✅ Startup Complete.")

# --- 4. AUTHENTICATION FUNCTION ---
async def get_api_key(api_key_token: str = Security(api_key_header)):
    """Verifies the API Key in the header."""
    if api_key_token == API_KEY:
        return api_key_token
    else:
        logging.warning(f"⛔ AUTH FAILED: Invalid Key attempted.")
        raise HTTPException(status_code=403, detail="⛔ Access Denied: Invalid API Key")

class PromptRequest(BaseModel):
    text: str
    max_new_tokens: int = 128
    temperature: float = 0.7

# --- 5. THE PROTECTED ROUTE ---
# We add 'dependencies=[Depends(get_api_key)]' to lock the door
@app.post("/generate", dependencies=[Depends(get_api_key)])
async def generate(data: PromptRequest):
    start = time.time()
    user_input = data.text
    
    # === 🛡️ PHASE 1: INPUT FILTERING ===
    
    # Layer 1: Regex
    safe, msg = security_engine.check_layer_1_regex(user_input)
    if not safe:
        logging.warning(f"BLOCKED L1: {msg}")
        return {"response": f"⛔ {msg}", "blocked": True}

    # Layer 1.5: DeBERTa (Injection)
    safe, msg = security_engine.check_layer_1_5_injection(user_input)
    if not safe:
        logging.warning(f"BLOCKED L1.5: {msg}")
        return {"response": f"⛔ {msg}", "blocked": True}

    # Layer 2: Llama Guard (Input)
    safe, msg = security_engine.check_layer_2_guard(user_input)
    if not safe:
        logging.warning(f"BLOCKED L2: {msg}")
        return {"response": f"⛔ {msg}", "blocked": True}

    # Layer 3: XML Escaping
    secure_prompt = security_engine.layer_3_escape(user_input)
    
    # === 🧠 PHASE 2: GENERATION ===
    
    # Construct strict system prompt
    final_prompt = f"""You are a helpful AI assistant.
User input data:
{secure_prompt}
Respond safely to the user."""

    response_text = llm_engine.generate(
        prompt=final_prompt, 
        max_tokens=data.max_new_tokens,
        temp=data.temperature
    )

    # === 🛡️ PHASE 3: OUTPUT FILTERING (New!) ===
    # We check if the AI said something bad
    # (Requires check_output method in security.py)
    if hasattr(security_engine, 'check_output'):
        safe_out, msg_out = security_engine.check_output(response_text, user_input)
        if not safe_out:
            logging.warning(f"BLOCKED OUTPUT: {msg_out}")
            return {
                "response": "⛔ Output Blocked: The model generated content violating safety policies.", 
                "latency": time.time()-start, 
                "blocked": True
            }

    # === ✅ SUCCESS ===
    latency = time.time() - start
    logging.info(f"SUCCESS: Latency {latency:.2f}s")
    
    return {
        "response": response_text,
        "latency": latency,
        "blocked": False
    }