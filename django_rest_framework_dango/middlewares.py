import threading
from typing import Any, Callable, Dict, Optional, TypedDict


class SessionData(TypedDict, total=False):
    # Define session data keys with types for auto-completion
    user_id: int
    username: str
    is_authenticated: bool


class SessionMiddleware:
    """Middleware to manage per-thread session data in a Django-like framework.

    This middleware initializes a session for each thread handling a request,
    stores the session in a thread-local dictionary, and cleans up the session
    data after the request is processed.

    Attributes:
        _sessions (Dict[threading.Thread, SessionData]): Thread-local session storage.
        get_response (Callable): The next middleware or view function in the stack.

    Methods:
        __call__(request): Handles the initialization, request processing, and cleanup of the session.
        _init_session(): Initializes a session for the current thread.
        _remove_session(): Removes the session data for the current thread.
        get_session(): Retrieves the session for the current thread, if available.
    """
    _sessions: Dict[threading.Thread, SessionData] = {}

    def __init__(self, get_response: Callable[[Any], Any]) -> None:
        """
        Initialize the SessionMiddleware.

        Args:
            get_response (Callable[[Any], Any]): The next middleware or view function.
        """
        self.get_response = get_response

    def __call__(self, request: Any) -> Any:
        """
        Process the request and manage session initialization and cleanup.

        Args:
            request (Any): The incoming HTTP request.

        Returns:
            Any: The response returned by the next middleware or view.
        """
        self._init_session()
        response = self.get_response(request)
        self._remove_session()
        return response

    def _init_session(self) -> None:
        """Initialize a new session for the current thread."""
        self._sessions[threading.current_thread()] = {}

    def _remove_session(self) -> None:
        """Remove the session for the current thread."""
        self._sessions.pop(threading.current_thread(), None)

    @classmethod
    def get_session(cls) -> Optional[SessionData]:
        """
        Retrieve the session for the current thread.

        Returns:
            Optional[SessionData]: The session data, or None if no session is active.
        """
        return cls._sessions.get(threading.current_thread())
