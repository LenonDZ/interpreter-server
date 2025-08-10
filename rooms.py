from typing import Dict, Set
from collections import defaultdict

class RoomHub:
    def __init__(self):
        self.rooms: Dict[str, Set] = defaultdict(set)

    def join(self, room_id: str, ws):
        self.rooms[room_id].add(ws)

    def leave(self, room_id: str, ws):
        if ws in self.rooms[room_id]:
            self.rooms[room_id].remove(ws)
        if not self.rooms[room_id]:
            del self.rooms[room_id]

    def peers(self, room_id: str, ws):
        return [p for p in self.rooms.get(room_id, set()) if p is not ws]

hub = RoomHub()
