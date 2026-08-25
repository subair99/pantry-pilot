# backend/scripts/reset_queue.py
import shutil
from pathlib import Path

# Point to the backend directory (parent of the scripts folder)
BASE_DIR = Path(__file__).parent.parent / "received_messages"

def reset_queue():
    channels = ["sms", "email", "voice"]
    total_moved = 0
    
    print("🔄 Resetting queue folders...\n")
    
    for channel in channels:
        processed_dir = BASE_DIR / channel / f"processed_{channel}"
        new_dir = BASE_DIR / channel / f"new_{channel}"
        
        # Ensure directories exist
        processed_dir.mkdir(parents=True, exist_ok=True)
        new_dir.mkdir(parents=True, exist_ok=True)
        
        files_moved = 0
        for file in processed_dir.iterdir():
            if file.is_file():
                # Smart revert: If it's a .txt.bak file, rename it back to .txt
                if file.suffix == ".bak" and file.stem.endswith(".txt"):
                    # e.g., "+15551112222_sarah.txt.bak" -> "+15551112222_sarah.txt"
                    target_name = file.stem 
                else:
                    target_name = file.name
                
                target_path = new_dir / target_name
                
                # Move the file
                shutil.move(str(file), str(target_path))
                files_moved += 1
                print(f"   📂 Moved: {file.name} -> {target_path.name}")
        
        total_moved += files_moved
        print(f"✅ Reset {channel.upper()}: Moved {files_moved} file(s) back to new_{channel}/\n")
        
    print(f"🎉 Queue reset complete! Total files restored: {total_moved}")
    print("💡 You can now run the demo or voice generator again.")

if __name__ == "__main__":
    reset_queue()