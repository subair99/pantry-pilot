# backend/scripts/generate_voice_from_docs.py
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import dashscope
from dashscope.audio.tts_v2 import *

# Load environment variables
load_dotenv()

# Configuration
DOCS_DIR = Path(__file__).parent.parent / "docs"
OUTPUT_DIR = Path(__file__).parent.parent / "received_messages" / "voice" / "new_voice"

QWEN_API_KEY = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")

# Use the officially documented CosyVoice model name
TTS_MODEL = "cosyvoice-v3-flash"

# Set the websocket API URL
dashscope.base_websocket_api_url = 'wss://dashscope-intl.aliyuncs.com/api-ws/v1/inference'

# Use the only guaranteed supported voice for cosyvoice-v3-flash on the international endpoint
DEFAULT_VOICE = "longanyang" 

def generate_voice_from_docs():
    if not QWEN_API_KEY:
        print("❌ ERROR: QWEN_API_KEY or DASHSCOPE_API_KEY not found in .env file!")
        print("Please add your API key to backend/.env")
        return

    # Set the API key for dashscope
    dashscope.api_key = QWEN_API_KEY
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Ensure docs directory exists
    if not DOCS_DIR.exists():
        print(f"ℹ️ Docs directory not found: {DOCS_DIR}")
        print("Please create the 'docs' folder and add your .txt files there.")
        return
        
    # Find all .txt files in the docs folder
    text_files = list(DOCS_DIR.glob("*.txt"))
    
    if not text_files:
        print("ℹ️ No .txt files found in the docs folder. Nothing to process.")
        return

    print(f" Found {len(text_files)} text file(s) to convert to voice using model: {TTS_MODEL}\n")

    for txt_file in text_files:
        print(f"📖 Reading: {txt_file.name}")
        
        try:
            # Read the text content
            text_content = txt_file.read_text(encoding="utf-8").strip()
            if not text_content:
                print(f"⚠️ Skipping {txt_file.name}: File is empty.")
                continue

            print(f"   Text: \"{text_content[:50]}...\"")
            print(f"   🎙️ Using Voice: {DEFAULT_VOICE}")
            print("   🔄 Generating audio...")

            # Instantiate SpeechSynthesizer 
            synthesizer = SpeechSynthesizer(
                model=TTS_MODEL, 
                voice=DEFAULT_VOICE,
                format=AudioFormat.WAV_24000HZ_MONO_16BIT # 24kHz is the native optimal rate for CosyVoice v3
            )
            
            # Call the API to get binary audio data (blocking call)
            audio_data = synthesizer.call(text_content)
            
            if audio_data:
                # Generate output filename (replace .txt with .wav)
                output_filename = txt_file.stem + ".wav"
                output_path = OUTPUT_DIR / output_filename
                
                # Save the binary audio data to file
                with open(output_path, "wb") as f:
                    f.write(audio_data)
                
                print(f"   ✅ Success! Saved as: {output_filename}\n")
            else:
                print(f"   ❌ Failed to get audio data for {txt_file.name}. Check API response.\n")
                
        except Exception as e:
            print(f"   ❌ Failed to process {txt_file.name}: {e}\n")

    print("🎉 Voice generation complete! Files are ready in received_messages/voice/new_voice/")
    print(" You can now click 'Process Queue & Refresh' in the UI.")

if __name__ == "__main__":
    generate_voice_from_docs()