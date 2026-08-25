# backend/test_qwen.py
import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# 1. Load environment variables
load_dotenv()

API_KEY = os.getenv("QWEN_API_KEY")
BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
MODEL = os.getenv("QWEN_MODEL", "qwen-plus")

print(f"🔑 API Key loaded: {'Yes' if API_KEY else 'No'}")
print(f"🌐 Base URL: {BASE_URL}")
print(f"🤖 Model: {MODEL}\n")

if not API_KEY:
    print("❌ ERROR: QWEN_API_KEY is missing from your .env file!")
    exit(1)

# 2. Initialize Client
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# 3. Define the structured output schema (exactly like your app)
class TestExtraction(BaseModel):
    donor_name: str = Field(description="Name of the person")
    item: str = Field(description="The item they are donating")

try:
    print("⏳ Sending request to Qwen API...")
    
    # 4. Make the API call with structured output
    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Extract the requested information into JSON."},
            {"role": "user", "content": "Hi, this is John. I am dropping off 12 boxes of pasta today."}
        ],
        response_format=TestExtraction
    )
    
    # 5. Print the result
    parsed_data = response.choices[0].message.parsed
    print("✅ SUCCESS! Qwen API is working perfectly.")
    print("\n📦 Extracted Data:")
    print(f"   - Donor Name: {parsed_data.donor_name}")
    print(f"   - Item: {parsed_data.item}")
    
except Exception as e:
    print(f"❌ FAILED! API returned an error:")
    print(f"   {e}")