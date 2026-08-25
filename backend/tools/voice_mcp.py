# backend/tools/voice_mcp.py
import os
import dashscope
from pathlib import Path
from typing import Dict, Any
from utils.logger import dispatch_logger, log_tool_execution

def transcribe_voice_to_text(audio_file_path: str = None) -> Dict[str, Any]:
    """
    Transcribes audio to text using Qwen's qwen3-asr-flash via DashScope MultiModalConversation API.
    """
    dispatch_logger.info(f"Attempting to transcribe voice input: {audio_file_path}")
    
    # Check both possible env var names
    api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    
    if not api_key:
        error_msg = "QWEN_API_KEY or DASHSCOPE_API_KEY not found. Please add it to your .env file."
        dispatch_logger.error(error_msg)
        return {"status": "error", "error_message": error_msg}
    
    if not audio_file_path or not os.path.exists(audio_file_path):
        error_msg = f"Audio file not found: {audio_file_path}"
        dispatch_logger.error(error_msg)
        return {"status": "error", "error_message": error_msg}

    try:
        # Configure DashScope
        dashscope.api_key = api_key
        dashscope.base_http_api_url = os.getenv(
            "DASHSCOPE_BASE_URL", 
            "https://dashscope-intl.aliyuncs.com/api/v1"
        )
        
        dispatch_logger.info("Calling Qwen MultiModalConversation ASR API (qwen3-asr-flash)...")
        
        # Format local file path for DashScope (requires file:// URI)
        # .resolve().as_uri() properly URL-encodes special characters like '+' to '%2B'
        file_uri = Path(audio_file_path).resolve().as_uri()
        dispatch_logger.info(f"Generated File URI: {file_uri}")
        
        messages = [
            {
                "role": "system",
                "content": [{"text": ""}]
            },
            {
                "role": "user",
                "content": [{"audio": file_uri}]
            }
        ]
        
        response = dashscope.MultiModalConversation.call(
            model="qwen3-asr-flash",
            messages=messages,
            result_format="message",
            asr_options={
                "enable_lid": True,
                "enable_itn": False
            }
        )
        
        if response.status_code == 200:
            # Extract text from the response structure
            content = response.output.choices[0].message.content
            transcribed_text = ""
            for item in content:
                if 'text' in item:
                    transcribed_text += item['text']
            
            dispatch_logger.info(f"Transcription successful: {transcribed_text}")
            
            success_response = {
                "status": "success",
                "transcribed_text": transcribed_text
            }
            log_tool_execution(dispatch_logger, "transcribe_voice", {"file": audio_file_path}, success_response)
            return success_response
        else:
            error_msg = f"Qwen ASR API error: {response.code} - {response.message}"
            dispatch_logger.error(error_msg)
            return {"status": "error", "error_message": error_msg}
            
    except Exception as e:
        dispatch_logger.error(f"Failed to transcribe voice: {e}")
        return {"status": "error", "error_message": str(e)}