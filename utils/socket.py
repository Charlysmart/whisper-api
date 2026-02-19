from typing import Dict, Set
from fastapi import WebSocket

connected_chat_users: Dict[int, WebSocket] = {}
connected_inbox_users: Dict[int, WebSocket] = {}
connected_notify_users: Dict[int, WebSocket] = {}
connected_anonymous_users: Dict[int, WebSocket] = {}
connected_room_users: Dict[str, Dict[int, Set[WebSocket]]] = {}