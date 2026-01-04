
import os
from dotenv import load_dotenv, find_dotenv

def debug_env():
    print("--- Debugging Environment ---")
    
    # 1. Check current directory
    print(f"Current Working Directory: {os.getcwd()}")
    
    # 2. Check for .env file presence
    env_path = find_dotenv()
    if env_path:
        print(f".env file found at: {env_path}")
    else:
        print("WARNING: No .env file found by python-dotenv!")
        # Fallback check manual
        if os.path.exists(".env"):
            print("  But '.env' exists in CWD via os.path.exists!")
        else:
            print("  And '.env' does NOT exist in CWD via os.path.exists.")

    # 3. Load env
    load_dotenv()
    
    # 4. Check Zoho Vars
    client_id = os.getenv("ZOHO_CLIENT_ID")
    client_secret = os.getenv("ZOHO_CLIENT_SECRET")
    
    if client_id:
        masked_id = client_id[:4] + "*" * (len(client_id)-4) if len(client_id) > 4 else "****"
        print(f"ZOHO_CLIENT_ID: Found ({masked_id})")
    else:
        print("ZOHO_CLIENT_ID: NOT SET or Empty")
        
    if client_secret:
        print("ZOHO_CLIENT_SECRET: Found (Masked)")
    else:
        print("ZOHO_CLIENT_SECRET: NOT SET or Empty")

if __name__ == "__main__":
    debug_env()
