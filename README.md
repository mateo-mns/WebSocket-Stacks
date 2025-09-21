# Sistema de Chat con WebSockets

Este proyecto implementa un sistema de chat en tiempo real utilizando WebSockets, con dos stacks diferentes para demostrar diferentes enfoques de implementación.

## 🚀 Características

- Comunicación en tiempo real con WebSockets
- Interfaz web moderna y responsive
- Soporte para múltiples usuarios simultáneos
- Indicadores de conexión y estado
- Soporte para acceso local y remoto
- Reconexión automática

## 📁 Estructura del Proyecto
WebSocket-Stacks/
├── stack1/ # Primera implementación
│ ├── server_websocket.py # Servidor WebSocket principal
│ ├── server_http.py # Servidor HTTP para el cliente
│ ├── client.html # Interfaz de usuario web
│ └── requirements.txt # Dependencias de Python
├── stack2/ # Segunda implementación
│ ├── server.py # Servidor único con aiohttp (HTTP + WebSocket)
│ ├── static/ # Archivos estáticos
│ │ ├── index.html # Interfaz de usuario
│ │ ├── client.js # Cliente JavaScript
│ │ └── styles.css # Estilos CSS
│ └── requirements.txt # Dependencias de Python
└── README.md


## 🛠️ Stack 1

### Tecnologías utilizadas
- **Backend**: Python 3.7+, asyncio, websockets
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Protocolos**: WebSocket, HTTP

### Funcionalidades
- Servidor WebSocket para comunicación bidireccional en tiempo real
- Servidor HTTP para servir la interfaz web
- Reconexión automática en caso de desconexión
- Indicadores visuales de estado de conexión
- Soporte para múltiples clientes simultáneos

### Instalación y uso

1. **Instalar dependencias**:
   cd stack1
   pip install -r requirements.txt

**Ejecucion**
- Ejecuta el servidor WebSocket --> python server_websocket.py
- Ejecuta el servidor HTTP en otra terminal --> python server_http.py
- Ejecuta el cliente en tu navegador --> http://localhost:8000/client.html


## 🛠️ Stack 2

### Tecnologías utilizadas
- **Backend**: Python 3.7+, aiohttp, asyncio
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Protocolos**: WebSocket, HTTP en el mismo puerto

### Funcionalidades
- Servidor único que maneja tanto HTTP como WebSockets
- Sistema de autenticación con tokens y cookies
- Interfaz más pulida con mejor diseño
- Manejo de sesiones de usuario
- Heartbeat para mantener conexiones activas


### Instalación y uso

1. **Instalar dependencias**:
   cd stack2
   pip install -r requirements.txt

**Ejecucion**
- Ejecuta el servidor --> python server.py
- Ejecuta el cliente en tu navegador --> http://localhost:8080

