"""
WebSocket endpoints for real-time updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import asyncio

from app.services.account_tracker import AccountTrackerService

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}  # account_id -> set of websockets
        self.active_group_connections: Dict[str, Set[WebSocket]] = {}  # group_id -> set of websockets

    async def connect(self, websocket: WebSocket, account_id: str):
        """Connect a WebSocket for an account."""
        await websocket.accept()
        if account_id not in self.active_connections:
            self.active_connections[account_id] = set()
        self.active_connections[account_id].add(websocket)

    async def connect_group(self, websocket: WebSocket, group_id: str):
        """Connect a WebSocket for a group."""
        await websocket.accept()
        if group_id not in self.active_group_connections:
            self.active_group_connections[group_id] = set()
        self.active_group_connections[group_id].add(websocket)

    def disconnect(self, websocket: WebSocket, account_id: str):
        """Disconnect a WebSocket."""
        if account_id in self.active_connections:
            self.active_connections[account_id].discard(websocket)
            if not self.active_connections[account_id]:
                del self.active_connections[account_id]

    def disconnect_group(self, websocket: WebSocket, group_id: str):
        """Disconnect a group WebSocket."""
        if group_id in self.active_group_connections:
            self.active_group_connections[group_id].discard(websocket)
            if not self.active_group_connections[group_id]:
                del self.active_group_connections[group_id]

    async def send_to_account(self, account_id: str, message: dict):
        """Send message to all WebSockets for an account."""
        if account_id in self.active_connections:
            disconnected = set()
            for websocket in self.active_connections[account_id]:
                try:
                    await websocket.send_json(message)
                except:
                    disconnected.add(websocket)
            # Clean up disconnected sockets
            for ws in disconnected:
                self.active_connections[account_id].discard(ws)

    async def send_to_group(self, group_id: str, message: dict):
        """Send message to all WebSockets for a group."""
        if group_id in self.active_group_connections:
            disconnected = set()
            for websocket in self.active_group_connections[group_id]:
                try:
                    await websocket.send_json(message)
                except:
                    disconnected.add(websocket)
            # Clean up disconnected sockets
            for ws in disconnected:
                self.active_group_connections[group_id].discard(ws)


manager = ConnectionManager()


@router.websocket("/{account_id}")
async def websocket_endpoint(websocket: WebSocket, account_id: str):
    """WebSocket endpoint for real-time account updates."""
    await manager.connect(websocket, account_id)
    try:
        while True:
            # Keep connection alive and handle any client messages
            data = await websocket.receive_text()
            # Echo back or handle client commands
            await websocket.send_json({"type": "ping", "data": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, account_id)


@router.websocket("/group/{group_id}")
async def websocket_group_endpoint(websocket: WebSocket, group_id: str):
    """WebSocket endpoint for real-time group updates."""
    await manager.connect_group(websocket, group_id)
    try:
        while True:
            # Keep connection alive and handle any client messages
            data = await websocket.receive_text()
            # Echo back or handle client commands
            await websocket.send_json({"type": "ping", "data": "pong"})
    except WebSocketDisconnect:
        manager.disconnect_group(websocket, group_id)

