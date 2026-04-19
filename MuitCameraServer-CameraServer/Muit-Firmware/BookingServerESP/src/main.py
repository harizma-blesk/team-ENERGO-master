from AppController import AppController
import time

app = AppController()

def setup():
    app.setup()

def loop():
    app.loop()

# Main loop
setup()
while True:
    loop()
    time.sleep(0.01)  # Small delay to prevent busy loop
