"""
Session Manager for FedEx Shipping Assistant.

Manages user sessions, conversation history, and state persistence.
"""

import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import defaultdict
from threading import Lock

from loguru import logger


@dataclass
class Message:
    """Single message in conversation history."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionState:
    """State for a user session."""
    session_id: str
    created_at: str
    last_activity: str
    messages: List[Message] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    request_count: int = 0


class SessionManager:
    """
    Manages user sessions for the shipping assistant.

    Features:
    - Session creation and retrieval
    - Conversation history tracking
    - Context persistence across requests
    - Session cleanup for inactive sessions
    """

    def __init__(
        self,
        session_timeout_minutes: int = 30,
        max_history_length: int = 20
    ):
        """
        Initialize Session Manager.

        Args:
            session_timeout_minutes: Minutes before inactive sessions expire
            max_history_length: Maximum messages to keep per session
        """
        self._sessions: Dict[str, SessionState] = {}
        self._lock = Lock()
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.max_history_length = max_history_length

        logger.info(
            f"SessionManager initialized (timeout={session_timeout_minutes}min, "
            f"max_history={max_history_length})"
        )

    def create_session(self, session_id: Optional[str] = None) -> SessionState:
        """
        Create a new session.

        Args:
            session_id: Optional custom session ID

        Returns:
            New SessionState
        """
        with self._lock:
            if session_id is None:
                session_id = str(uuid.uuid4())[:12]

            now = datetime.now().isoformat()
            session = SessionState(
                session_id=session_id,
                created_at=now,
                last_activity=now
            )

            self._sessions[session_id] = session
            logger.info(f"Created session: {session_id}")

            return session

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """
        Get an existing session.

        Args:
            session_id: Session identifier

        Returns:
            SessionState if found and not expired, None otherwise
        """
        with self._lock:
            session = self._sessions.get(session_id)

            if session is None:
                return None

            # Check expiration
            last_activity = datetime.fromisoformat(session.last_activity)
            if datetime.now() - last_activity > self.session_timeout:
                logger.info(f"Session {session_id} expired")
                del self._sessions[session_id]
                return None

            return session

    def get_or_create_session(self, session_id: Optional[str] = None) -> SessionState:
        """
        Get existing session or create new one.

        Args:
            session_id: Optional session ID

        Returns:
            SessionState
        """
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session

        return self.create_session(session_id)

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a message to session history.

        Args:
            session_id: Session identifier
            role: "user" or "assistant"
            content: Message content
            metadata: Optional message metadata

        Returns:
            True if message added, False if session not found
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return False

            message = Message(
                role=role,
                content=content,
                metadata=metadata or {}
            )

            session.messages.append(message)
            session.last_activity = datetime.now().isoformat()
            session.request_count += 1

            # Trim history if needed
            if len(session.messages) > self.max_history_length:
                session.messages = session.messages[-self.max_history_length:]

            return True

    def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session identifier
            limit: Maximum messages to return

        Returns:
            List of message dictionaries
        """
        session = self.get_session(session_id)
        if session is None:
            return []

        messages = session.messages
        if limit:
            messages = messages[-limit:]

        return [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp,
                "metadata": m.metadata
            }
            for m in messages
        ]

    def update_context(
        self,
        session_id: str,
        key: str,
        value: Any
    ) -> bool:
        """
        Update session context.

        Args:
            session_id: Session identifier
            key: Context key
            value: Context value

        Returns:
            True if updated, False if session not found
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return False

            session.context[key] = value
            session.last_activity = datetime.now().isoformat()

            return True

    def get_context(
        self,
        session_id: str,
        key: Optional[str] = None
    ) -> Any:
        """
        Get session context.

        Args:
            session_id: Session identifier
            key: Optional specific key to get

        Returns:
            Context value or entire context dict
        """
        session = self.get_session(session_id)
        if session is None:
            return None if key else {}

        if key:
            return session.context.get(key)

        return session.context.copy()

    def clear_context(self, session_id: str) -> bool:
        """Clear session context."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return False

            session.context = {}
            session.last_activity = datetime.now().isoformat()

            return True

    def end_session(self, session_id: str) -> bool:
        """
        End and remove a session.

        Args:
            session_id: Session identifier

        Returns:
            True if session was removed
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                logger.info(f"Ended session: {session_id}")
                return True
            return False

    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions.

        Returns:
            Number of sessions removed
        """
        with self._lock:
            now = datetime.now()
            expired = []

            for session_id, session in self._sessions.items():
                last_activity = datetime.fromisoformat(session.last_activity)
                if now - last_activity > self.session_timeout:
                    expired.append(session_id)

            for session_id in expired:
                del self._sessions[session_id]

            if expired:
                logger.info(f"Cleaned up {len(expired)} expired sessions")

            return len(expired)

    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about active sessions."""
        with self._lock:
            total_sessions = len(self._sessions)
            total_messages = sum(
                len(s.messages) for s in self._sessions.values()
            )
            total_requests = sum(
                s.request_count for s in self._sessions.values()
            )

            return {
                "active_sessions": total_sessions,
                "total_messages": total_messages,
                "total_requests": total_requests,
                "avg_messages_per_session": (
                    total_messages / total_sessions if total_sessions > 0 else 0
                )
            }


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get or create the global session manager."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
