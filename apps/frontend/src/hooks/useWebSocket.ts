import { useEffect, useRef, useState } from 'react'

interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

export function useWebSocket(url: string) {
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Convert relative URL to WebSocket URL
    const wsUrl = url.startsWith('http')
      ? url.replace('http', 'ws')
      : `ws://localhost:8000${url}`

    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      setIsConnected(true)
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setLastMessage(data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.onclose = () => {
      setIsConnected(false)
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        if (wsRef.current?.readyState === WebSocket.CLOSED) {
          // Reconnection will be handled by useEffect
        }
      }, 3000)
    }

    wsRef.current = ws

    return () => {
      ws.close()
    }
  }, [url])

  return { lastMessage, isConnected }
}

