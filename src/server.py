#!/usr/bin/env python3
import http.server
import socketserver
import os
import webbrowser

PORT = 8080
DIRECTORY = "/a0/instruments/custom/iskala"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

if __name__ == "__main__":
    os.chdir(DIRECTORY)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌺 ISKALA сервер запущено!")
        print(f"📱 Відкрийте: http://localhost:{PORT}/standalone.html")
        print(f"🌱 Або: http://localhost:{PORT}/index.html")
        print("🛑 Натисніть Ctrl+C для зупинки")

        # Open browser
        webbrowser.open(f'http://localhost:{PORT}/standalone.html')

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("
🛑 Сервер зупинено")
