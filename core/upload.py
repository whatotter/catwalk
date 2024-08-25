import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
import datetime

allowedAuth = []
websock = False
filename = str(datetime.datetime.now())+".bin"
port = 11932

# Define a custom request handler
class FileUploadHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.headers['Authorization'] not in allowedAuth:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'Invalid auth token.')
            print("[X] invalid auth")
            return

        content_length = int(self.headers['Content-Length'])
        uploaded_file = self.rfile.read(content_length)

        # Specify the directory where you want to save the file
        save_path = './uploads/'+self.headers['Authorization']  # Change this to your desired directory

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        fileDir = os.path.join(save_path, self.headers['filename'])

        if ".." in self.headers['filename']: # this is a path traversal attack most likely, just back out immediately
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'File uploaded successfully.')

        with open(fileDir, 'wb') as f:
            f.write(uploaded_file)

        if websock: websock.send({"upload": fileDir})

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'File uploaded successfully.')

    def do_GET(self):
        if self.headers['Authorization'] not in allowedAuth:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'Invalid auth token.')
            print("[X] invalid auth")
            return

        root = os.getcwd()

        if websock: websock.send({"download": ""})

        # Set the directory to serve files from
        self.directory = os.path.join(root, 'uploads')  # Change 'files' to your desired directory

        # Continue with the default behavior of serving files
        super().do_GET()

#httpd = HTTPServer(('0.0.0.0', port), FileUploadHandler)
