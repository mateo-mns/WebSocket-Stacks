import http.server
import socketserver
import webbrowser
import socket


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Headers para permitir CORS (importante para desarrollo)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Manejar preflight requests para CORS
        self.send_response(200)
        self.end_headers()

def get_local_ips():
    """Obtener todas las IPs locales usando socket"""
    ips = ['127.0.0.1']  # Siempre incluir localhost
    
    try:
        # Obtener el nombre de host
        host_name = socket.gethostname()
        
        # Obtener todas las IPs asociadas al host
        host_ips = socket.gethostbyname_ex(host_name)[2]
        
        # Filtrar y agregar IPs únicas
        for ip in host_ips:
            if ip not in ips and not ip.startswith('127.'):
                ips.append(ip)
                
    except Exception as e:
        print(f"Error al obtener IPs: {e}")
    
    return ips

def get_public_ip():
    """Intentar obtener la IP pública (puede no funcionar en todas las redes)"""
    try:
        # Crear un socket temporal para conectarse a un servidor externo
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # Conectar a Google DNS
            return s.getsockname()[0]
    except:
        return "No se pudo determinar"

def main():
    PORT = 8000
    
    # Obtener IPs locales
    local_ips = get_local_ips()
    
    with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
        print("=" * 60)
        print("Servidor HTTP iniciado")
        print("=" * 60)
        print(f"URL local: http://localhost:{PORT}/static/index.html")
        
        for ip in local_ips:
            if ip != '127.0.0.1':
                print(f"URL en red local: http://{ip}:{PORT}/static/index.html")
        
        # Intentar obtener IP pública
        public_ip = get_public_ip()
        if public_ip != "No se pudo determinar":
            print(f"URL para acceso externo: http://{public_ip}:{PORT}/static/index.html")
        else:
            print("No se pudo determinar la IP pública automáticamente.")
        
        print("=" * 60)
        print("Para acceso externo, necesitas:")
        print("1. Configurar reenvío de puertos en tu router")
        print("2. Conocer tu IP pública (puedes verla en https://whatismyipaddress.com/)")
        print("3. Conectar usando: http://[IP_PUBLICA]:{PORT}/static/index.html")
        print("=" * 60)
        
        # Abrir automáticamente en el navegador
        webbrowser.open(f'http://localhost:{PORT}/static/index.html')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor HTTP detenido")

if __name__ == "__main__":
    main()