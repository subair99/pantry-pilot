# backend/tools/voice_mcp.py
import os
import logging
from typing import Dict, Any
from utils.logger import dispatch_logger, log_tool_execution

# Optional: Real OpenAI Whisper integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

def transcribe_voice_to_text(audio_file_path: str = None, audio_base64: str = None) -> Dict[str, Any]:
    """
    Transcribes audio to text. 
    Uses OpenAI Whisper if available, otherwise uses a deterministic mock for the demo.
    """
    dispatch_logger.info("Attempting to transcribe voice input...")
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # 🛡️ HACKATHON DEMO SAFETY NET
    if not OPENAI_AVAILABLE or not openai_api_key or not audio_file_path:
        dispatch_logger.warning("OpenAI Whisper credentials missing or no file. Using mock transcription.")
        
        # Deterministic mock based on a known demo scenario
        mock_transcription = "Hi PantryPilot, this is John. Dropping off 12 boxes of pasta and 20 lbs of apples at 5 PM."
        
        mock_response = {
            "status": "success",
            "transcribed_text": mock_transcription,
            "note": "Mocked for demo reliability. Add OPENAI_API_KEY to use real Whisper transcription."
        }
        log_tool_execution(dispatch_logger, "transcribe_voice", {}, mock_response)
        return mock_response

    # 🚀 REAL OPENAI WHISPER EXECUTION
    try:
        client = OpenAI(api_key=openai_api_key)
        with open(audio_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        success_response = {
            "status": "success",
            "transcribed_text": transcription.text
        }
        log_tool_execution(dispatch_logger, "transcribe_voice", {}, success_response)
        return success_response
        
    except Exception as e:
        error_response = {"status": "error", "error_message": str(e)}
        dispatch_logger.error(f"Failed to transcribe voice: {e}")
        return error_response