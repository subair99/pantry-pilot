# backend/tools/voice_mcp.py
import os
import dashscope
from typing import Dict, Any
from utils.logger import dispatch_logger, log_tool_execution

def transcribe_voice_to_text(audio_file_path: str = None) -> Dict[str, Any]:
    dispatch_logger.info(f"Attempting to transcribe voice input: {audio_file_path}")
    
    # 1. Read Main API Key
    api_key = os.getenv("MAIN_API_KEY")
    
    # 2. Read ASR-specific Model Name and Base URL from .env (with safe fallbacks)
    asr_model = os.getenv("ASR_MODEL", "qwen3-asr-flash")
    base_url = os.getenv("ASR_BASE_URL", "https://dashscope-intl.aliyuncs.com/api/v1")
    
    if not api_key:
        error_msg = "MAIN_API_KEY not found. Please add it to your .env file."
        dispatch_logger.error(error_msg)
        return {"status": "error", "error_message": error_msg}
    
    if not audio_file_path or not os.path.exists(audio_file_path):
        error_msg = f"Audio file not found: {audio_file_path}"
        dispatch_logger.error(error_msg)
        return {"status": "error", "error_message": error_msg}

    try:
        # 3. Configure DashScope using the .env variables
        dashscope.api_key = api_key
        dashscope.base_http_api_url = base_url
        
        dispatch_logger.info(f"Calling MultiModalConversation ASR API (Model: {asr_model})...")
        
        from pathlib import Path
        file_uri = Path(audio_file_path).resolve().as_uri()
        
        messages = [
            {"role": "system", "content": [{"text": ""}]},
            {"role": "user", "content": [{"audio": file_uri}]}
        ]
        
        # 4. Use the asr_model variable
        response = dashscope.MultiModalConversation.call(
            model=asr_model,
            messages=messages,
            result_format="message",
            asr_options={"enable_lid": True, "enable_itn": False}
        )
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            transcribed_text = "".join([item['text'] for item in content if 'text' in item])
            
            dispatch_logger.info(f"Transcription successful: {transcribed_text}")
            
            success_response = {"status": "success", "transcribed_text": transcribed_text}
            log_tool_execution(dispatch_logger, "transcribe_voice", {"file": audio_file_path}, success_response)
            return success_response
        else:
            error_msg = f"ASR API error: {response.code} - {response.message}"
            dispatch_logger.error(error_msg)
            return {"status": "error", "error_message": error_msg}
            
    except Exception as e:
        dispatch_logger.error(f"Failed to transcribe voice: {e}")
        return {"status": "error", "error_message": str(e)}