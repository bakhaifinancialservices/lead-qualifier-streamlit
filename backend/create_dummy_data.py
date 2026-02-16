import requests
import random
from datetime import datetime, timedelta

API_URL = "http://localhost:8000"

# Diverse lead templates
LEAD_TEMPLATES = [
    # High-quality leads (score 70-90)
    {
        "name": "Rajesh Kumar",
        "email": "rajesh{n}@example.com",
        "phone": "98765432{n:02d}",
        "initial_message": "I want to invest {amount} lakhs for retirement in {years} years. I am {age} years old and work in {industry}.",
        "source": "web",
        "params": {
            "amount": [20, 25, 30, 40, 50],
            "years": [10, 15, 20],
            "age": [35, 40, 45, 50],
            "industry": ["IT", "finance", "manufacturing", "healthcare"]
        }
    },
    {
        "name": "Priya Sharma",
        "email": "priya{n}@example.com",
        "phone": "91234567{n:02d}",
        "initial_message": "Looking to invest {amount} lakhs in mutual funds for {purpose}. Can you help?",
        "source": "referral",
        "params": {
            "amount": [10, 15, 20, 25],
            "purpose": ["wealth creation", "child education", "buying a house", "long term growth"]
        }
    },
    {
        "name": "Amit Patel",
        "email": "amit{n}@example.com",
        "phone": "99887766{n:02d}",
        "initial_message": "Need urgent tax planning. Financial year ending soon. Have {amount} lakhs to save tax under Section 80C and 80D.",
        "source": "web",
        "params": {
            "amount": [5, 8, 10, 12, 15]
        }
    },
    
    # Medium-quality leads (score 40-69)
    {
        "name": "Sunita Reddy",
        "email": "sunita{n}@example.com",
        "phone": "98761234{n:02d}",
        "initial_message": "Recently {event}. Need financial planning advice. Monthly income is {income} lakhs.",
        "source": "social_media",
        "params": {
            "event": ["married", "had a baby", "changed jobs", "started business"],
            "income": ["0.5", "0.8", "1", "1.2"]
        }
    },
    {
        "name": "Vikram Singh",
        "email": "vikram{n}@example.com",
        "phone": "99008877{n:02d}",
        "initial_message": "Business owner. Want to invest profits from my {business_type} business.",
        "source": "referral",
        "params": {
            "business_type": ["manufacturing", "retail", "software", "consulting", "real estate"]
        }
    },
    
    # Low-quality leads (score <40)
    {
        "name": "Rahul{n}",
        "email": "rahul{n}@example.com",
        "phone": "91234500{n:02d}",
        "initial_message": "Want to start investing. Just started working.",
        "source": "web",
        "params": {}
    },
    {
        "name": "Neha{n}",
        "email": "neha{n}@example.com",
        "phone": "99998888{n:02d}",
        "initial_message": "Tell me about investment",
        "source": "web",
        "params": {}
    },
]

def create_lead(template, index):
    """Create a single lead from template"""
    
    # Replace {n} with index
    name = template['name'].format(n=index)
    email = template['email'].format(n=index)
    phone = template['phone'].format(n=index)
    source = template['source']
    
    # Build message with random params
    message = template['initial_message']
    if template.get('params'):
        for key, values in template['params'].items():
            value = random.choice(values)
            message = message.replace(f"{{{key}}}", str(value))
    
    message = message.format(n=index)
    
    # Create lead
    data = {
        "name": name,
        "email": email,
        "phone": phone,
        "initial_message": message,
        "source": source
    }
    
    try:
        response = requests.post(f"{API_URL}/api/leads", json=data, timeout=30)
        
        if response.status_code == 201:
            lead = response.json()
            print(f"✓ Created lead {index}: {name} (Score: {lead.get('quality_score', 'N/A')})")
            return True
        else:
            print(f"✗ Failed lead {index}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error creating lead {index}: {e}")
        return False


def create_dummy_data(num_leads=50):
    """Create multiple dummy leads"""
    
    print(f"\n🚀 Creating {num_leads} dummy leads...\n")
    
    successful = 0
    failed = 0
    
    for i in range(1, num_leads + 1):
        # Pick random template
        template = random.choice(LEAD_TEMPLATES)
        
        # Create lead
        if create_lead(template, i):
            successful += 1
        else:
            failed += 1
        
        # Small delay to avoid overwhelming API
        import time
        time.sleep(0.5)
    
    print(f"\n" + "="*50)
    print(f"✅ Successfully created: {successful} leads")
    print(f"❌ Failed: {failed} leads")
    print(f"="*50)
    
    # Show stats
    try:
        stats_response = requests.get(f"{API_URL}/api/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"\n📊 Database Statistics:")
            print(f"   Total Leads: {stats['total']}")
            print(f"   Hot (70+): {stats['hot']}")
            print(f"   Warm (40-69): {stats['warm']}")
            print(f"   Cold (<40): {stats['cold']}")
            print(f"   Fraud: {stats['fraud']}")
    except:
        pass


if __name__ == "__main__":
    import sys
    
    # Check if number provided
    if len(sys.argv) > 1:
        try:
            num = int(sys.argv[1])
            create_dummy_data(num)
        except ValueError:
            print("Usage: python create_dummy_data.py [number_of_leads]")
            print("Example: python create_dummy_data.py 50")
    else:
        # Default: 30 leads
        create_dummy_data(30)