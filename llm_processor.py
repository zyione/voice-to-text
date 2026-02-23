import requests

class LLMProcessor:
    def __init__(self, settings_manager):
        self.settings = settings_manager
        self.api_url = "http://localhost:11434/api/generate"

    def process(self, text):
        if not text or not text.strip():
            return text
            
        if not self.settings.get("use_llm"):
            return text

        prompt = self.settings.get("llm_prompt")
        full_prompt = f"{prompt}\n\n{text}"
        
        print(f"Sending to Ollama (llama3)...")
        try:
            response = requests.post(self.api_url, json={
                "model": "llama3",
                "prompt": full_prompt,
                "stream": False
            }, timeout=10)
            
            if response.status_code == 200:
                result = response.json().get("response", "")
                if result:
                    print(f"Ollama processed result: {result}")
                    return result.strip()
            else:
                print(f"Ollama error: {response.text}")
        except Exception as e:
            print(f"Failed to connect to Ollama: {e}")
            
        print("Falling back to raw transcription.")
        return text

