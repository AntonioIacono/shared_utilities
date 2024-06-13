import socket
import http.server
import os
import time
import base64

class MJPEGFileServer(http.server.BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            decoded_data = base64.b64decode(post_data)

            output_directory = 'files'
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

            filename = os.path.join(output_directory, 'frame.jpg')
            with open(filename, 'wb') as file:
                file.write(decoded_data)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Frame salvato correttamente.")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Errore durante il salvataggio del frame: {str(e)}".encode())

    def do_GET(self):
        try:
            # Specifica il percorso della directory contenente i frame JPEG
            frame_directory = 'frames'

            # Controlla se la directory dei frame esiste
            if not os.path.exists(frame_directory):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Directory dei frame non trovata.")
                return

            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=--frameboundary')
            self.end_headers()

            while True:
                for filename in sorted(os.listdir(frame_directory)):
                    if filename.endswith(".jpg"):
                        filepath = os.path.join(frame_directory, filename)
                        with open(filepath, 'rb') as file:
                            frame = file.read()

                        self.wfile.write(b"--frameboundary\r\n")
                        self.wfile.write(b"Content-Type: image/jpeg\r\n")
                        self.wfile.write(b"Content-Length: " + str(len(frame)).encode() + b"\r\n")
                        self.wfile.write(b"\r\n")
                        self.wfile.write(frame)
                        self.wfile.write(b"\r\n")
                        
                        # Attendi un breve intervallo di tempo prima di inviare il prossimo frame
                        time.sleep(0.1)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Errore durante lo streaming del video: {str(e)}".encode())

if __name__ == '__main__':
    server_address = ('', 8080)  # Cambia la porta se necessario
    httpd = http.server.HTTPServer(server_address, MJPEGFileServer)
    
    # Set the socket option for DSCP
    DSCP_VALUE = 0xa4  # DSCP 7 is equivalent to binary 00111000, which is 0x1C
    httpd.socket.setsockopt(socket.SOL_IP, socket.IP_TOS, DSCP_VALUE)
    
    # Configura il socket per riutilizzare l'indirizzo
    httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    print(f"Server in ascolto sulla porta {server_address[1]}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer interrotto.")
        httpd.server_close()
