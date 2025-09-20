document.addEventListener('DOMContentLoaded', function() {
    const statusElement = document.getElementById('status');
    const connectionDetails = document.getElementById('connectionDetails');
    const chatContainer = document.getElementById('chatContainer');
    const usernameInput = document.getElementById('username');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const usersCountElement = document.getElementById('usersCount');
    const serverInfoElement = document.getElementById('serverInfo');
    
    let socket;
    let isConnected = false;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 10;
    const reconnectDelay = 3000; // 3 segundos
    
    // Determinar la URL del servidor WebSocket
    function getWebSocketUrl() {
        // Si estamos en localhost, usar localhost
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'ws://localhost:8765';
        }
        // De lo contrario, usar el mismo host pero diferente puerto
        return `ws://${window.location.hostname}:8765`;
    }
    
    const websocketUrl = getWebSocketUrl();
    serverInfoElement.textContent = `Servidor: ${websocketUrl}`;
    
    // Conectar al servidor WebSocket
    connect();
    
    function connect() {
        try {
            connectionDetails.textContent = `Conectando a ${websocketUrl}...`;
            
            // Intentar conectar con el servidor
            socket = new WebSocket(websocketUrl);
            
            socket.onopen = function(event) {
                console.log('Conexión establecida con el servidor');
                updateConnectionStatus('Conectado', 'connected');
                connectionDetails.textContent = `Conectado a ${websocketUrl}`;
                messageInput.disabled = false;
                sendButton.disabled = false;
                isConnected = true;
                reconnectAttempts = 0;
                
                addMessage({
                    tipo: 'sistema',
                    usuario: 'Sistema',
                    mensaje: 'Conectado al servidor correctamente',
                    timestamp: new Date().toISOString()
                });
            };
            
            socket.onmessage = function(event) {
                try {
                    const messageData = JSON.parse(event.data);
                    addMessage(messageData);
                    
                    // Actualizar contador de usuarios si está disponible
                    if (messageData.usuarios_conectados !== undefined) {
                        usersCountElement.textContent = messageData.usuarios_conectados;
                    }
                } catch (e) {
                    console.error('Error al procesar mensaje:', e);
                }
            };
            
            socket.onerror = function(error) {
                console.error('Error en la conexión WebSocket:', error);
                updateConnectionStatus('Error de conexión', 'disconnected');
                connectionDetails.textContent = `Error conectando a ${websocketUrl}`;
            };
            
            socket.onclose = function(event) {
                console.log('Conexión cerrada');
                updateConnectionStatus('Desconectado', 'disconnected');
                connectionDetails.textContent = 'Conexión cerrada. Reconectando...';
                messageInput.disabled = true;
                sendButton.disabled = true;
                isConnected = false;
                
                // Intentar reconectar con retroceso exponencial
                if (reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++;
                    const delay = reconnectDelay * Math.pow(1.5, reconnectAttempts);
                    setTimeout(connect, delay);
                } else {
                    connectionDetails.textContent = 'No se pudo reconectar. Recarga la página para intentarlo de nuevo.';
                }
            };
            
        } catch (error) {
            console.error('Error al crear WebSocket:', error);
            updateConnectionStatus('Error', 'disconnected');
            connectionDetails.textContent = `Error: ${error.message}`;
            
            // Intentar reconectar después de un delay
            setTimeout(connect, reconnectDelay);
        }
    }
    
    function updateConnectionStatus(text, status) {
        statusElement.textContent = text;
        statusElement.className = `status ${status}`;
    }
    
    function addMessage(data) {
        const messageElement = document.createElement('div');
        
        // Formatear la fecha
        const date = new Date(data.timestamp);
        const timeString = date.toLocaleTimeString();
        
        if (data.tipo === 'sistema') {
            messageElement.className = 'message system';
            messageElement.innerHTML = `
                <div class="message-header">
                    <span>${data.usuario}</span>
                    <span>${timeString}</span>
                </div>
                <div>${data.mensaje}</div>
            `;
        } else if (data.tipo === 'error') {
            messageElement.className = 'message system';
            messageElement.innerHTML = `
                <div class="message-header">
                    <span>Error</span>
                    <span>${timeString}</span>
                </div>
                <div>${data.mensaje}</div>
            `;
        } else {
            // Determinar si es un mensaje entrante o saliente
            const isOutgoing = data.usuario === usernameInput.value;
            messageElement.className = `message ${isOutgoing ? 'outgoing' : 'incoming'}`;
            
            let ipInfo = '';
            if (data.ip_remitente && !isOutgoing) {
                ipInfo = `<small>(${data.ip_remitente})</small>`;
            }
            
            messageElement.innerHTML = `
                <div class="message-header">
                    <span class="user-badge">${data.usuario} ${ipInfo}</span>
                    <span>${timeString}</span>
                </div>
                <div>${data.mensaje}</div>
            `;
        }
        
        chatContainer.appendChild(messageElement);
        // Scroll al último mensaje
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Enviar mensaje al hacer clic en el botón
    sendButton.addEventListener('click', sendMessage);
    
    // Enviar mensaje al presionar Enter
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    function sendMessage() {
        const message = messageInput.value.trim();
        const username = usernameInput.value.trim() || 'Usuario';
        
        if (message && isConnected) {
            const messageData = {
                tipo: 'mensaje',
                usuario: username,
                mensaje: message,
                timestamp: new Date().toISOString()
            };
            
            // Enviar mensaje al servidor
            socket.send(JSON.stringify(messageData));
            
            // Limpiar el campo de entrada
            messageInput.value = '';
        }
    }
});