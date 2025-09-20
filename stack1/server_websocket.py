import asyncio
import websockets
import json
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Almacenar todas las conexiones activas
conexiones = set()

async def manejar_conexion(websocket):
    """Maneja cada nueva conexión de cliente"""
    # Obtener información del cliente
    client_ip, client_port = websocket.remote_address
    logger.info(f"Nueva conexión desde {client_ip}:{client_port}")
    
    # Agregar la nueva conexión
    conexiones.add(websocket)
    logger.info(f"Conexiones activas: {len(conexiones)}")
    
    try:
        # Notificar a todos los usuarios sobre el nuevo miembro
        mensaje_bienvenida = {
            "tipo": "sistema",
            "usuario": "Sistema",
            "mensaje": f"¡Nuevo usuario conectado desde {client_ip}!",
            "timestamp": datetime.now().isoformat(),
            "usuarios_conectados": len(conexiones)
        }
        await broadcast(mensaje_bienvenida)
        
        # Enviar mensaje de bienvenida al nuevo cliente
        mensaje_bienvenida_personal = {
            "tipo": "sistema",
            "usuario": "Sistema",
            "mensaje": f"Bienvenido al chat! Tu IP: {client_ip}",
            "timestamp": datetime.now().isoformat(),
            "usuarios_conectados": len(conexiones)
        }
        await websocket.send(json.dumps(mensaje_bienvenida_personal))
        
        # Escuchar mensajes del cliente
        async for mensaje in websocket:
            try:
                datos = json.loads(mensaje)
                datos["timestamp"] = datetime.now().isoformat()
                datos["ip_remitente"] = client_ip
                datos["usuarios_conectados"] = len(conexiones)
                
                logger.info(f"Mensaje recibido de {client_ip}: {datos.get('usuario', 'Anónimo')}: {datos.get('mensaje', '')}")
                
                # Reenviar el mensaje a todos los clientes conectados
                await broadcast(datos)
                
            except json.JSONDecodeError:
                error_msg = {
                    "tipo": "error",
                    "mensaje": "Formato de mensaje inválido",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(error_msg))
                logger.warning(f"Mensaje con formato inválido desde {client_ip}")
            
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Conexión cerrada por {client_ip}")
    except Exception as e:
        logger.error(f"Error con {client_ip}: {str(e)}")
    finally:
        # Eliminar la conexión cuando se cierra
        if websocket in conexiones:
            conexiones.remove(websocket)
            logger.info(f"Conexión eliminada. Total: {len(conexiones)}")
            
            # Notificar a todos los usuarios sobre la desconexión
            mensaje_despedida = {
                "tipo": "sistema",
                "usuario": "Sistema",
                "mensaje": f"Un usuario desde {client_ip} ha abandonado el chat.",
                "timestamp": datetime.now().isoformat(),
                "usuarios_conectados": len(conexiones)
            }
            await broadcast(mensaje_despedida)

async def broadcast(mensaje):
    """Envía un mensaje a todos los clientes conectados"""
    if conexiones:
        mensaje_json = json.dumps(mensaje)
        # Usar gather para enviar a todos simultáneamente
        await asyncio.gather(
            *[conexion.send(mensaje_json) for conexion in conexiones],
            return_exceptions=True  # Para evitar que una excepción detenga todo
        )

async def health_check(path, request_headers):
    """Maneja solicitudes de health check"""
    if path == "/health":
        return http.HTTPStatus.OK, [], b"OK\n"

async def main():
    """Función principal para iniciar el servidor"""
    logger.info("Iniciando servidor WebSocket...")
    
    # Configurar el servidor para escuchar en todas las interfaces
    server = await websockets.serve(
        manejar_conexion, 
        "0.0.0.0",  # Escuchar en todas las interfaces
        8765,       # Puerto
        ping_interval=20,  # Mantener conexiones activas
        ping_timeout=120,  # Tiempo antes de considerar una conexión como muerta
        # process_request=health_check  # Para health checks HTTP
    )
    
    logger.info(f"Servidor WebSocket iniciado en ws://0.0.0.0:8765")
    logger.info("El servidor está listo para conexiones locales y externas")
    
    # Mantener el servidor ejecutándose
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"Error al iniciar el servidor: {str(e)}")