import os
import time

# Clean up
os.system("pkill -f streamlit")

# Run App
print("🚀 Starting Streamlit...")
os.system("nohup streamlit run app.py --server.port=8501 --server.address=127.0.0.1 > /content/logs.txt 2>&1 &")

# Wait
time.sleep(5)

# Tunnel
print("🔗 CLICK THE LINK BELOW (ending in .trycloudflare.com):")
!/content/cloudflared tunnel --url http://127.0.0.1:8501