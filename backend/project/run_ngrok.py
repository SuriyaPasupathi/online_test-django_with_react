import os
from pyngrok import ngrok, conf

# Ngrok config (specifies path to ngrok executable)
config = conf.PyngrokConfig(ngrok_path="C:\\ngrok\\ngrok.exe")

# Start tunnel to localhost:8000
public_url = ngrok.connect(8000, pyngrok_config=config)

# Print the tunnel public URL
print("Public URL:", public_url)



