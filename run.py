
from app.app import create_app
app = create_app()

if __name__ == "__main__":
    app.run(host='192.168.1.242', port=5000)