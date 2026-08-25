# backend/tools/file_queue.py
import os
import shutil
from pathlib import Path
from utils.logger import orchestrator_logger

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
            try:
                text = file.read_text(encoding="utf-8")
                
                # Extract phone number from filename (e.g., "+15551112222_sarah.txt" -> "+15551112222")
                donor_phone = file.stem.split('_')[0] if file.stem.startswith('+') else None
                
                orchestrator.process_incoming_message(
                    text, 
                    donor_phone=donor_phone, 
                    source="SMS"
                )
                
                shutil.move(str(file), str(BASE_DIR / "sms" / "processed_sms" / file.name))
                processed_count += 1
                orchestrator_logger.info(f"Processed SMS: {file.name}")
            except Exception as e:
                orchestrator_logger.error(f"Error processing SMS {file.name}: {e}")

    # 2. Process Email (Text files, filename can be donor@example.com.txt)
    email_dir = BASE_DIR / "email" / "new_email"
    for file in sorted(email_dir.iterdir()):
        if file.is_file() and file.suffix == '.txt':
            try:
                text = file.read_text(encoding="utf-8")
                # Use filename as email if it contains '@', otherwise None
                donor_email = file.stem if "@" in file.stem else None
                orchestrator.process_incoming_message(text, donor_email=donor_email, source="Email")
                shutil.move(str(file), str(BASE_DIR / "email" / "processed_email" / file.name))
                processed_count += 1
                orchestrator_logger.info(f"Processed Email: {file.name}")
            except Exception as e:
                orchestrator_logger.error(f"Error processing Email {file.name}: {e}")

    # 3. Process Voice (Audio files)
    voice_dir = BASE_DIR / "voice" / "new_voice"
    for file in sorted(voice_dir.iterdir()):
        if file.is_file() and file.suffix in ['.webm', '.wav', '.mp3', '.m4a']:
            try:
                # Transcribe using the provided function
                result = transcribe_func(str(file))
                if result["status"] == "success":
                    orchestrator.process_incoming_message(result["transcribed_text"], source="Voice")
                else:
                    orchestrator_logger.warning(f"Voice transcription failed for {file.name}: {result.get('error_message')}")
                
                shutil.move(str(file), str(BASE_DIR / "voice" / "processed_voice" / file.name))
                processed_count += 1
                orchestrator_logger.info(f"Processed Voice: {file.name}")
            except Exception as e:
                orchestrator_logger.error(f"Error processing Voice {file.name}: {e}")
                
    return processed_count