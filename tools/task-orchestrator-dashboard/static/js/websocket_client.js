/**
 * WebSocket Client for Real-Time Updates
 * Manages WebSocket connection and broadcasts updates to components
 */

class WebSocketClient {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
        this.listeners = new Map();
        this.isConnected = false;
        this.reconnectTimer = null;
    }

    /**
     * Connect to WebSocket server
     */
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        console.log('Connecting to WebSocket:', wsUrl);

        try {
            this.ws = new WebSocket(wsUrl);
            this.setupEventHandlers();
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.handleConnectionFailure();
        }
    }

    /**
     * Setup WebSocket event handlers
     */
    setupEventHandlers() {
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus(true);
            this.emit('connected', {});
        };

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                console.log('WebSocket message received:', message);
                this.handleMessage(message);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        this.ws.onclose = (event) => {
            console.log('WebSocket disconnected:', event.code, event.reason);
            this.isConnected = false;
            this.updateConnectionStatus(false);
            this.emit('disconnected', { code: event.code, reason: event.reason });

            // Attempt to reconnect
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.scheduleReconnect();
            } else {
                console.warn('Max reconnect attempts reached. Falling back to polling.');
                this.emit('fallback_to_polling', {});
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.emit('error', { error });
        };
    }

    /**
     * Handle incoming WebSocket messages
     */
    handleMessage(message) {
        const { type, data, timestamp } = message;

        switch (type) {
            case 'connection_established':
                console.log('WebSocket connection confirmed:', message.message || 'Connected');
                this.emit('connection_established', message);
                break;

            case 'database_update':
                this.emit('database_update', data);
                break;

            case 'task_update':
                this.emit('task_update', data);
                break;

            case 'feature_update':
                this.emit('feature_update', data);
                break;

            case 'project_update':
                this.emit('project_update', data);
                break;

            case 'connection_count':
                this.emit('connection_count', data);
                break;

            case 'ping':
                this.send({ type: 'pong', timestamp: Date.now() });
                break;

            default:
                console.warn('Unknown message type:', type);
                this.emit('unknown_message', message);
        }
    }

    /**
     * Schedule reconnection attempt
     */
    scheduleReconnect() {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

        this.reconnectTimer = setTimeout(() => {
            this.connect();
        }, delay);
    }

    /**
     * Handle connection failure
     */
    handleConnectionFailure() {
        this.isConnected = false;
        this.updateConnectionStatus(false);

        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
        } else {
            this.emit('fallback_to_polling', {});
        }
    }

    /**
     * Send message to server
     */
    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            try {
                this.ws.send(JSON.stringify(message));
                return true;
            } catch (error) {
                console.error('Failed to send WebSocket message:', error);
                return false;
            }
        } else {
            console.warn('WebSocket not connected. Cannot send message.');
            return false;
        }
    }

    /**
     * Register event listener
     */
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    /**
     * Unregister event listener
     */
    off(event, callback) {
        if (!this.listeners.has(event)) return;

        const callbacks = this.listeners.get(event);
        const index = callbacks.indexOf(callback);
        if (index > -1) {
            callbacks.splice(index, 1);
        }
    }

    /**
     * Emit event to all registered listeners
     */
    emit(event, data) {
        if (!this.listeners.has(event)) return;

        const callbacks = this.listeners.get(event);
        callbacks.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`Error in event listener for '${event}':`, error);
            }
        });
    }

    /**
     * Update connection status UI
     */
    updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('connection-status');
        const statusText = document.getElementById('connection-text');

        if (statusIndicator) {
            if (connected) {
                statusIndicator.classList.remove('disconnected');
                if (statusText) statusText.textContent = 'Connected';
            } else {
                statusIndicator.classList.add('disconnected');
                if (statusText) {
                    if (this.reconnectAttempts < this.maxReconnectAttempts) {
                        statusText.textContent = 'Reconnecting...';
                    } else {
                        statusText.textContent = 'Disconnected';
                    }
                }
            }
        }
    }

    /**
     * Disconnect WebSocket
     */
    disconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }

        if (this.ws) {
            this.ws.close(1000, 'Client disconnect');
            this.ws = null;
        }

        this.isConnected = false;
        this.reconnectAttempts = 0;
    }

    /**
     * Check if WebSocket is connected
     */
    isReady() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }

    /**
     * Get connection state
     */
    getState() {
        if (!this.ws) return 'DISCONNECTED';

        const states = {
            [WebSocket.CONNECTING]: 'CONNECTING',
            [WebSocket.OPEN]: 'CONNECTED',
            [WebSocket.CLOSING]: 'CLOSING',
            [WebSocket.CLOSED]: 'DISCONNECTED'
        };

        return states[this.ws.readyState] || 'UNKNOWN';
    }
}

// Create global WebSocket client instance
const wsClient = new WebSocketClient();

// Auto-connect on page load
window.addEventListener('DOMContentLoaded', () => {
    wsClient.connect();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    wsClient.disconnect();
});
