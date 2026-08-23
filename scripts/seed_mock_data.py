# scripts/seed_mock_data.py
import urllib.request
import urllib.error
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def seed_mock_data():
    print("🌱 Seeding 10 realistic mock donations (5 SMS, 5 Email) for PantryPilot demo...")
    print("⚠️  Make sure your backend server is running (uv run uvicorn main:app --reload)\n")
    
    sms_donations = [
        {"message": "Hi, this is Sarah from the local bakery. Dropping off 50 loaves of bread at 8 AM today.", "donor_phone": "+15551112222", "donor_email": None},
        {"message": "Mike's Farm here. We have 100 lbs of fresh tomatoes for you this afternoon.", "donor_phone": "+15553334444", "donor_email": None},
        {"message": "Hi PantryPilot, this is John. Dropping off 12 boxes of pasta and 20lbs of apples at 5 PM.", "donor_phone": "+15555556666", "donor_email": None},
        {"message": "David from community garden. 30 bags of organic potatoes ready for pickup tomorrow morning.", "donor_phone": "+15557778888", "donor_email": None},
        {"message": "Lisa here. I have 15 containers of prepared meals and 10 gallons of milk to drop off at 6 PM.", "donor_phone": "+15559990000", "donor_email": None}
    ]
    
    email_donations = [
        {"message": "Hello PantryPilot Team, I am writing to arrange a donation of 200 canned goods from the Downtown Grocery Store. We can deliver this Thursday at 10 AM. Best, Robert.", "donor_email": "robert@downtowngrocery.com", "donor_phone": None},
        {"message": "Dear Coordinator, Our church group has collected 50 winter coats and 30 blankets. We would like to drop them off at the main center this Friday evening. Sincerely, Pastor Mark.", "donor_email": "mark@stmaryschurch.org", "donor_phone": None},
        {"message": "Hi there, This is Jennifer from the Tech Corp cafeteria. We have 40 untouched catering trays from yesterday's event that we'd love to donate. Available for pickup anytime today. Thanks!", "donor_email": "jennifer@techcorp.com", "donor_phone": None},
        {"message": "Greetings, I am a local farmer and I have a surplus of 150 lbs of zucchini and squash. I can bring them to the loading dock tomorrow morning at 9 AM. Regards, Thomas.", "donor_email": "thomas@valleyfarms.net", "donor_phone": None},
        {"message": "Hello, The Rotary Club is hosting a food drive this weekend. We expect to have about 100 boxes of non-perishable items ready for your team to collect on Sunday at 2 PM. Best, Amanda.", "donor_email": "amanda@rotaryclub.org", "donor_phone": None}
    ]
    
    all_donations = sms_donations + email_donations
    
    for i, donation in enumerate(all_donations):
        channel = "📱 SMS" if donation["donor_phone"] else "📧 Email"
        print(f"[{i+1}/10] Processing ({channel}): '{donation['message'][:60]}...'")
        
        data = json.dumps(donation).encode('utf-8')
        req = urllib.request.Request(
            f"{BASE_URL}/api/process-donation",
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                # Check if the backend returned the expected success payload
                if "agent_response" in result:
                    first_line = result['agent_response'].split('\n')[0]
                    print(f"✅ Success: {first_line}\n")
                else:
                    # This will print the EXACT error message from the backend
                    print(f"❌ Backend returned an error: {result.get('message', result)}\n")
                    
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"❌ HTTP Error {e.code}: {error_body}\n")
        except urllib.error.URLError as e:
            print(f"❌ Error: Could not connect to backend. Is the server running? ({e})\n")
            return
        except Exception as e:
            print(f"❌ Unexpected Error: {e}\n")
            
        time.sleep(0.3)
        
    print("🎉 Seeding complete!")

if __name__ == "__main__":
    seed_mock_data()