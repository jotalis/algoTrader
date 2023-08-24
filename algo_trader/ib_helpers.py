import os

def cleanup_files():
    if os.path.exists("bot_running.txt"): os.remove("bot_running.txt")
    if os.path.exists("contract_request.txt"): os.remove("contract_request.txt")

def check_buy():
    os.path.exists("bot_running.txt")