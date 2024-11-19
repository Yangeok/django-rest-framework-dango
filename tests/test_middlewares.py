from threading import current_thread
from typing import Any

import pytest

from django_rest_framework_dango.middlewares import SessionMiddleware


@pytest.fixture
def get_response_mock():
    """Mock for the get_response function."""
    def mock_response(request: Any):
        return {"message": "success"}
    return mock_response


@pytest.fixture
def middleware(get_response_mock):
    """Fixture for SessionMiddleware."""
    return SessionMiddleware(get_response_mock)


def test_session_middleware_initializes_and_removes_session(middleware):
    # given: A middleware instance and a mock request
    request = {}

    # when: The middleware processes the request
    response = middleware(request)

    # then: A session should be created and removed after processing
    assert response == {"message": "success"}
    assert current_thread() not in middleware._sessions


def test_session_data_can_be_accessed_and_modified(middleware):
    # given: A middleware instance
    middleware._init_session()
    session = middleware.get_session()

    # when: Session data is modified
    assert session is not None
    session["user_id"] = 1
    session["username"] = "test_user"
    session["is_authenticated"] = True

    # then: Session data should match the expected values
    assert session["user_id"] == 1
    assert session["username"] == "test_user"
    assert session["is_authenticated"] is True

    # Cleanup
    middleware._remove_session()


def test_init_session_overwrites_existing_session(middleware):
    # given: A middleware instance with an already initialized session
    middleware._init_session()
    first_session = middleware.get_session()
    first_session["user_id"] = 42

    # when: The session is re-initialized
    middleware._init_session()
    second_session = middleware.get_session()

    # then: The previous session data should be overwritten
    assert second_session is not None
    assert second_session != first_session
    assert "user_id" not in second_session

    # Cleanup
    middleware._remove_session()


def test_remove_session_noop_if_no_session(middleware):
    # given: A middleware instance with no active session
    middleware._remove_session()

    # then: No error should occur
    assert middleware.get_session() is None


def test_get_session_returns_none_if_no_session(middleware):
    # given: A middleware instance

    # when: No session is initialized
    session = middleware.get_session()

    # then: The result should be None
    assert session is None


def test_full_middleware_flow(middleware):
    # given: A mock request
    request = {}

    # when: The middleware processes a request
    response = middleware(request)

    # then: The flow should initialize and clean up session
    assert response == {"message": "success"}
    assert middleware.get_session() is None
