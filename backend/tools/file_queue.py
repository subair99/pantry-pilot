# backend/tools/file_queue.py
import os
import shutil
import time
from pathlib import Path
from utils.logger import orchestrator_logger
from utils.metrics import metrics

BASE_DIR = Path(__file__).parent.parent / "received_messages"

def ensure_dirs():
    """Ensures all queue directories exist."""
    for channel in ["sms", "email", "voice"]:
        for status in ["new", "processed"]:
            (BASE_DIR / channel / f"{status}_{channel}").mkdir(parents=True, exist_ok=True)

def process_queue(orchestrator, transcribe_func):
    """
    Scans new_* folders in order (SMS -> Email -> Voice), 
    processes them, and moves them to processed_* folders.
    """
    ensure_dirs()
    processed_count = 0
    
    # 1. Process SMS (Text files)
    sms_dir = BASE_DIR / "sms" / "new_sms"
    for file in sorted(sms_dir.iterdir()):
        if file.is_file() and file.suffix == '.txt':
            start_time = time.time()
            try:
                text = file.read_text(encoding="utf-8")
                donor_phone = file.stem.split('_')[0] if file.stem.startswith('+') else None
                
                orchestrator.process_incoming_message(
                    text, 
                    donor_phone=donor_phone, 
                    source="SMS"
                )
                
                shutil.move(str(file), str(BASE_DIR / "sms" / "processed_sms" / file.name))
                processed_count += 1
                
                # ✅ RECORD METRICS FOR EACH MESSAGE
                latency = (time.time() - start_time) * 1000
                metrics.record_request("SMS_Intake", True, latency)
                
                orchestrator_logger.info(f"Processed SMS: {file.name}")
            except Exception as e:
                latency = (time.time() - start_time) * 1000
                metrics.record_request("SMS_Intake", False, latency)
                orchestrator_logger.error(f"Error processing SMS {file.name}: {e}")

    # 2. Process Email (Text files)
    email_dir = BASE_DIR / "email" / "new_email"
    for file in sorted(email_dir.iterdir()):
        if file.is_file() and file.suffix == '.txt':
            start_time = time.time()
            try:
                text = file.read_text(encoding="utf-8")
                donor_email = file.stem if "@" in file.stem else None
                orchestrator.process_incoming_message(text, donor_email=donor_email, source="Email")
                shutil.move(str(file), str(BASE_DIR / "email" / "processed_email" / file.name))
                processed_count += 1
                
                # ✅ RECORD METRICS FOR EACH MESSAGE
                latency = (time.time() - start_time) * 1000
                metrics.record_request("Email_Intake", True, latency)
                
                orchestrator_logger.info(f"Processed Email: {file.name}")
            except Exception as e:
                latency = (time.time() - start_time) * 1000
                metrics.record_request("Email_Intake", False, latency)
                orchestrator_logger.error(f"Error processing Email {file.name}: {e}")

    # 3. Process Voice (Audio files)
    voice_dir = BASE_DIR / "voice" / "new_voice"
    for file in sorted(voice_dir.iterdir()):
        if file.is_file() and file.suffix in ['.webm', '.wav', '.mp3', '.m4a']:
            start_time = time.time()
            try:
                # Transcribe using the provided function
                result = transcribe_func(str(file))
                
                # Extract phone number from filename
                donor_phone = file.stem.split('_')[0] if file.stem.startswith('+') else None
                
                if result["status"] == "success":
                    # DEBUG: Print what was transcribed
                    print(f"\n🎤 DEBUG - File: {file.name}")
                    print(f" Transcribed Text: {result['transcribed_text']}")
                    print(f"📞 Extracted Phone: {donor_phone}\n")
                    
                    orchestrator.process_incoming_message(
                        result["transcribed_text"], 
                        donor_phone=donor_phone,
                        source="Voice"
                    )
                    # ✅ ONLY move the file if transcription was successful!
                    shutil.move(str(file), str(BASE_DIR / "voice" / "processed_voice" / file.name))
                    
                    # ✅ RECORD METRICS FOR EACH MESSAGE
                    latency = (time.time() - start_time) * 1000
                    metrics.record_request("Voice_Intake", True, latency)
                else:
                    orchestrator_logger.warning(f"Voice transcription failed for {file.name}: {result.get('error_message')}")
                    # Do NOT move the file if it failed, so it stays in 'new_voice' for retry!
                    latency = (time.time() - start_time) * 1000
                    metrics.record_request("Voice_Intake", False, latency)
                
                processed_count += 1
                orchestrator_logger.info(f"Processed Voice: {file.name}")
            except Exception as e:
                latency = (time.time() - start_time) * 1000
                metrics.record_request("Voice_Intake", False, latency)
                orchestrator_logger.error(f"Error processing Voice {file.name}: {e}")
                
    return processed_count