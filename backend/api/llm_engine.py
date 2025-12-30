import os
from llama_cpp import Llama

class LLMEngine:
    def __init__(self, model_filename: str):
        """
        Initializes the Llama-cpp model.
        """
        # Construct path to the models directory (one level up from 'api')
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_path, "models", model_filename)

        print(f" Loading model from: {model_path}...", flush=True)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f" Model file not found at: {model_path}")
        
        # Load the model into RAM (or VRAM if GPU is configured)
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,          
            n_threads=6,        
            n_gpu_layers=-1,     
            verbose=False        # Keep logs clean
        )
        print(" Model loaded successfully.")

    def generate(self, prompt: str, max_tokens: int = 128, temp: float = 0.7):
        """
        Generates a response using ChatML formatting (Standard for Qwen).
        """
        # Qwen ChatML Template: <|im_start|>user\n{msg}<|im_end|>\n<|im_start|>assistant\n
        formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

        output = self.llm(
            formatted_prompt,
            max_tokens=max_tokens,
            stop=["<|im_end|>"], # Stop exactly when the model finishes its turn
            temperature=temp,
            echo=False           # Do not return the input prompt in the output
        )
        
        return output["choices"][0]["text"].strip()