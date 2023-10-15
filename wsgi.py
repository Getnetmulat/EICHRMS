"""Application entry point."""
from App import app

if __name__ == "__main__":
    app.run(host='localhost', debug='False', port=int("80")) #port 80 is the default port you can change what you can you use
