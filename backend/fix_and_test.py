import os
import sys
from dotenv import load_dotenv
from groq import Groq

print("="*60)
print("🔍 Diagnosing Groq AI Issue")
print("="*60)

# Load environment
load_dotenv()

# Check 1: API Key
print("\n1. Checking API Key...")
api_key = os.getenv('GROQ_API_KEY')
if api_key and api_key != 'your_groq_api_key_here':
    print(f"   ✓ API Key found: {api_key[:10]}...{api_key[-4:]}")
else:
    print("   ❌ API Key NOT found or placeholder in .env file!")
    print("   Fix: Add GROQ_API_KEY to backend/.env (get one at https://console.groq.com)")
    sys.exit(1)

# Check 2: Package installed
print("\n2. Checking openai package...")
try:
    from groq import Groq
    print("   ✓ Package installed")
except ImportError:
    print("   ❌ Package NOT installed!")
    print("   Fix: pip install openai")
    sys.exit(1)

# Check 3: Can connect to Groq
print("\n3. Testing Groq connection...")
try:
    client = Groq(
        api_key=api_key,
    )
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": "Say 'OK'"}],
    )
    print(f"   ✓ Groq responded: {response.choices[0].message.content.strip()}")
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    sys.exit(1)

# Check 4: Test actual qualification
print("\n4. Testing lead qualification...")
try:
    from app.services.groq_ai import qualify_lead

    result = qualify_lead("I want to invest 20 lakhs for retirement in 10 years")

    print(f"   ✓ Qualification successful!")
    print(f"     Goal: {result['goal']}")
    print(f"     Timeline: {result['timeline']}")
    print(f"     Budget: {result['budget_range']}")
    print(f"     Score: {result['quality_score']}")

    if result['goal'] == 'unclear' and result['quality_score'] == 30:
        print("\n   ⚠️  WARNING: Got default values - AI might not be analyzing properly")
    else:
        print("\n   ✓ AI is analyzing correctly!")

except Exception as e:
    print(f"   ❌ Qualification failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ All checks passed! Groq AI is working correctly.")
print("="*60)
