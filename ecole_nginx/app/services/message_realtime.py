# app/services/message_realtime.py — diffusion temps réel des messages
"""Hub WebSocket de la messagerie, un par worker.

L'API tourne sous gunicorn avec plusieurs workers (docker-compose.yml) et
sans Redis (ni en Docker, ni dans l'installation Windows) : un message
envoyé via le worker A doit pourtant atteindre un destinataire connecté au
worker B. Chaque worker interroge donc la table messages (id > dernier id
vu, une requête indexée par seconde) tant qu'il a au moins une connexion
ouverte, et pousse les nouveaux messages à SES connexions. Latence ≈ 1 s,
aucune dépendance supplémentaire."""

import asyncio
import logging
from collections import defaultdict
from typing import Dict, Set

from fastapi import WebSocket
from starlette.concurrency import run_in_threadpool

from app.database import SessionLocal
from app.Models.MMessages import Message

logger = logging.getLogger(__name__)

POLL_INTERVAL = 1.0


def serialize_message(m: Message) -> dict:
    return {
        "id": m.id,
        "sender_id": m.sender_id,
        "recipient_id": m.recipient_id,
        "body": m.body,
        "read_at": m.read_at.isoformat() if m.read_at else None,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


class MessageHub:
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        self.last_id = None
        self._task = None

    async def connect(self, user_id: str, ws: WebSocket):
        self.connections[user_id].add(ws)
        if self._task is None or self._task.done():
            if self.last_id is None:
                self.last_id = await run_in_threadpool(self._max_id)
            self._task = asyncio.create_task(self._poll_loop())

    def disconnect(self, user_id: str, ws: WebSocket):
        conns = self.connections.get(user_id)
        if conns:
            conns.discard(ws)
            if not conns:
                self.connections.pop(user_id, None)

    async def _send(self, user_id: str, payload: dict):
        for ws in list(self.connections.get(user_id, ())):
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(user_id, ws)

    @staticmethod
    def _max_id() -> int:
        db = SessionLocal()
        try:
            last = db.query(Message.id).order_by(Message.id.desc()).first()
            return last[0] if last else 0
        finally:
            db.close()

    def _fetch_new(self, after_id: int):
        db = SessionLocal()
        try:
            rows = (
                db.query(Message)
                .filter(Message.id > after_id)
                .order_by(Message.id)
                .limit(500)
                .all()
            )
            return [serialize_message(m) for m in rows]
        finally:
            db.close()

    async def _poll_loop(self):
        # S'arrête de lui-même quand plus personne n'est connecté sur ce worker
        while self.connections:
            try:
                nouveaux = await run_in_threadpool(self._fetch_new, self.last_id)
                for msg in nouveaux:
                    self.last_id = max(self.last_id, msg["id"])
                    payload = {"type": "message", "message": msg}
                    await self._send(msg["recipient_id"], payload)
                    # L'expéditeur aussi : ses autres onglets/appareils
                    if msg["sender_id"] != msg["recipient_id"]:
                        await self._send(msg["sender_id"], payload)
            except Exception as e:
                logger.error(f"Messagerie temps réel : erreur de lecture des messages : {e}")
            await asyncio.sleep(POLL_INTERVAL)


hub = MessageHub()
