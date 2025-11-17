from google import genai
import os

api_key = os.getenv("GEMINI_API_KEY")

class Gemini:
    def __init__(self, model, api_key):
        self.model = model
        self.api_key = api_key



