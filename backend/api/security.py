import os
import re
import torch
from transformers import pipeline
from llama_cpp import Llama

class SecurityEngine:
    def __init__(self, guard_model_filename: str):
        """
        Initializes all security layers (Regex, DeBERTa, Llama Guard).
        """
        print("🛡️  Initializing Security Engine...", flush=True)
        
        # --- LAYER 1: REGEX PATTERNS ---
        self.jailbreak_patterns = [
            re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE),
            re.compile(r"you\s+are\s+now\s+(an?\s+)?(unrestricted|jailbroken|free)", re.IGNORECASE),
            re.compile(r"system\s*[:]\s*", re.IGNORECASE),
            re.compile(r"override\s+protocol", re.IGNORECASE),
        ]

        # --- LAYER 1.5: DEBERTA (Prompt Injection) ---
        print("   - Loading DeBERTa Injection Classifier...", flush=True)
        try:
            # We use device=-1 for CPU to save GPU VRAM for the main LLM
            self.injection_pipeline = pipeline(
                "text-classification", 
                model="protectai/deberta-v3-base-prompt-injection", 
                device=-1 
            )
        except Exception as e:
            print(f"⚠️ Warning: Could not load DeBERTa: {e}")
            self.injection_pipeline = None

        # --- LAYER 2: LLAMA GUARD (Safety Policy) ---
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        guard_path = os.path.join(base_path, "models", guard_model_filename)

        if os.path.exists(guard_path):
            print(f"   - Loading Llama Guard from {guard_model_filename}...", flush=True)
            self.guard_model = Llama(
                model_path=guard_path,
                n_ctx=2048,
                n_threads=4,
                verbose=False
            )
        else:
            print(f"❌ ERROR: Llama Guard model missing at {guard_path}")
            self.guard_model = None

        print("✅ Security Engine Ready.")

    def check_layer_1_regex(self, text: str):
        """Regex Sanitization"""
        for pattern in self.jailbreak_patterns:
            if pattern.search(text):
                return False, "Blocked by Layer 1 (Regex): Jailbreak pattern detected."
        if len(text) > 2000:
            return False, "Blocked by Layer 1 (Length): Input too long."
        return True, "Pass"

    def check_layer_1_5_injection(self, text: str):
        """DeBERTa Injection Detection"""
        if not self.injection_pipeline:
            return True, "Skipped (Model not loaded)"
        
        result = self.injection_pipeline(text)[0]
        if result['label'] == "INJECTION" and result['score'] > 0.9:
            return False, f"Blocked by Layer 1.5 (DeBERTa): Injection detected ({result['score']:.2f})"
        
        return True, "Pass"

    def check_layer_2_guard(self, text: str):
        """Llama Guard Safety Check"""
        if not self.guard_model:
            return True, "Skipped (Model not loaded)"

        # Strict Llama Guard 3 Template
        guard_prompt = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>
Task: Check if there is unsafe content in 'User' messages in conversations according our safety policy with the below categories.
<BEGIN UNSAFE CONTENT CATEGORIES>
S1: Violent Crimes. 
S2: Non-Violent Crimes. 
S3: Sex-Related Crimes. 
S4: Child Sexual Exploitation. 
S5: Defamation. 
S6: Specialized Advice. 
S7: Privacy. 
S8: Intellectual Property. 
S9: Indiscriminate Weapons. 
S10: Hate. 
S11: Suicide & Self-Harm. 
S12: Sexual Content. 
S13: Elections.
<END UNSAFE CONTENT CATEGORIES>

<BEGIN CONVERSATION>
User: {text}
<END CONVERSATION>

Provide your safety assessment for ONLY THE LAST User message in the above conversation:
- First line must read 'safe' or 'unsafe'.
- If unsafe, a second line must include a comma-separated list of violated categories.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

        output = self.guard_model(
            guard_prompt, 
            max_tokens=20, 
            temperature=0.0, 
            echo=False
        )
        result = output["choices"][0]["text"].strip().lower()
        
        if "unsafe" in result:
            return False, f"Blocked by Layer 2 (Llama Guard): Content flagged as UNSAFE. ({result})"
        
        return True, "Pass"

    def layer_3_escape(self, text: str):
        """Wraps input in XML tags"""
        escaped = text.replace('"', '\\"').replace("<", "&lt;").replace(">", "&gt;")
        return f"<user_input>\n{escaped}\n</user_input>"