import http.server
import base64
import os

class Base64FileServer(http.server.BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            decoded_data = base64.b64decode(post_data)

            # Cambia la directory di destinazione per salvare i file
            output_directory = 'files'
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

            filename = os.path.join(output_directory, 'file_received.docx')
            with open(filename, 'wb') as file:
                file.write(decoded_data)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"File salvato correttamente.")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Errore durante il salvataggio del file: {str(e)}".encode())

if __name__ == '__main__':
    server_address = ('', 80)  # Indirizzo IP e porta del server
    httpd = http.server.HTTPServer(server_address, Base64FileServer)

    print("Server in ascolto sulla porta 80...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer interrotto.")
        httpd.server_close()
