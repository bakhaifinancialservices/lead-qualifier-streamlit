import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
print(f"Using API Key: {api_key[:20]}...")

genai.configure(api_key=api_key)

print("\n📋 Available Gemini Models:\n")
print("="*60)

try:
    models = genai.list_models()
    
    found_models = []
    for model in models:
        # Check if model supports generateContent
        if 'generateContent' in model.supported_generation_methods:
            found_models.append(model.name)
            print(f"✓ {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description[:80]}...")
            print()
    
    if not found_models:
        print("❌ No models found that support generateContent!")
    else:
        print("="*60)
        print(f"\n✅ Found {len(found_models)} usable models")
        print("\nUse one of these in your gemini_ai.py:")
        for model_name in found_models:
            # Extract just the model part (remove 'models/' prefix)
            short_name = model_name.replace('models/', '')
            print(f"  model = genai.GenerativeModel('{short_name}')")

except Exception as e:
    print(f"❌ Error listing models: {e}")
    print("\nThis might mean:")
    print("1. Your API key is invalid")
    print("2. You need to enable the API at: https://aistudio.google.com")
    print("3. Your region doesn't have access to Gemini yet")