import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "MOSY C2 Master Server is Running Successfully!"

if __name__ == '__main__':
    # Render avtomatik beradigan PORT ni oladi (default 10000 yoki boshqa)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)