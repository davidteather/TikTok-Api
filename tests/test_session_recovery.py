"""
Test session recovery functionality for TikTokApi

These tests verify that the API can detect and recover from dead browser sessions.
"""

import pytest
import asyncio
import os
from TikTokApi import TikTokApi
from playwright.async_api import Error as PlaywrightError


# Test configuration
@pytest.fixture
def ms_token():
    """Get ms_token from environment or return None"""
    return os.getenv("ms_token", None)


@pytest.fixture
def headless():
    """Get headless setting from environment, default to True"""
    headless_env = os.getenv("headless", "true").lower()
    return headless_env in ("true", "1", "yes")


@pytest.mark.asyncio
async def test_session_validation(headless, ms_token):
    """Test that session validation correctly identifies valid sessions"""
    api = TikTokApi()
    ms_tokens = [ms_token] if ms_token else None
    await api.create_sessions(num_sessions=2, headless=headless, ms_tokens=ms_tokens)

    try:
        # All sessions should be valid initially
        for session in api.sessions:
            is_valid = await api._is_session_valid(session)
            assert is_valid, "Newly created session should be valid"

        # Close one session manually and mark as invalid
        session_to_kill = api.sessions[0]
        await session_to_kill.page.close()
        await session_to_kill.context.close()
        session_to_kill.is_valid = False  # Mark as invalid

        # First session should now be invalid
        is_valid = await api._is_session_valid(session_to_kill)
        assert not is_valid, "Closed session should be invalid"

        # Second session should still be valid
        is_valid = await api._is_session_valid(api.sessions[1])
        assert is_valid, "Untouched session should still be valid"

    finally:
        await api.close_sessions()
        await api.stop_playwright()


@pytest.mark.asyncio
async def test_mark_session_invalid(headless, ms_token):
    """Test that marking a session as invalid works correctly"""
    api = TikTokApi()
    ms_tokens = [ms_token] if ms_token else None
    await api.create_sessions(num_sessions=1, headless=headless, ms_tokens=ms_tokens)

    try:
        session = api.sessions[0]
        assert session.is_valid, "New session should be valid"

        # Mark as invalid
        await api._mark_session_invalid(session)

        assert not session.is_valid, "Session should be marked invalid"

        # Should not be able to use the page anymore
        is_valid = await api._is_session_valid(session)
        assert not is_valid, "Validation should confirm session is invalid"

    finally:
        await api.close_sessions()
        await api.stop_playwright()


@pytest.mark.asyncio
async def test_get_valid_session_with_all_valid(headless, ms_token):
    """Test getting a valid session when all are healthy"""
    api = TikTokApi()
    ms_tokens = [ms_token] if ms_token else None
    await api.create_sessions(num_sessions=3, headless=headless, ms_tokens=ms_tokens)

    try:
        # Should successfully get a valid session
        idx, session = await api._get_valid_session_index()

        assert idx is not None
        assert session is not None
        assert session.is_valid
        assert await api._is_session_valid(session)

    finally:
        await api.close_sessions()
        await api.stop_playwright()


@pytest.mark.asyncio
async def test_get_valid_session_with_some_dead(headless, ms_token):
    """Test getting a valid session when some are dead"""
    api = TikTokApi()
    ms_tokens = [ms_token] if ms_token else None
    await api.create_sessions(num_sessions=3, headless=headless, ms_tokens=ms_tokens)

    try:
        # Kill first two sessions
        await api.sessions[0].page.close()
        await api.sessions[0].context.close()
        api.sessions[0].is_valid = False

        await api.sessions[1].page.close()
        await api.sessions[1].context.close()
        api.sessions[1].is_valid = False

        # Should still get the third valid session
        idx, session = await api._get_valid_session_index()

        assert idx == 2, "Should return the only valid session (index 2)"
        assert session == api.sessions[2]
        assert await api._is_session_valid(session)

    finally:
        await api.close_sessions()
        await api.stop_playwright()


@pytest.mark.asyncio
async def test_get_valid_session_with_all_dead(headless, ms_token):
    """Test getting a valid session when all are dead"""
    api = TikTokApi()
    ms_tokens = [ms_token] if ms_token else None
    await api.create_sessions(num_sessions=2, headless=headless, ms_tokens=ms_tokens)

    try:
        # Kill all sessions
        for session in api.sessions:
            await session.page.close()
            await session.context.close()
            session.is_valid = False

        # Should raise an exception
        with pytest.raises(Exception, match="No valid sessions available"):
            await api._get_valid_session_index()

    finally:
        await api.close_sessions()
        await api.stop_playwright()


@pytest.mark.asyncio
async def test_recover_sessions(headless, ms_token):
    """Test that session recovery removes dead sessions"""
    api = TikTokApi()
    ms_tokens = [ms_token] if ms_token else None
    await api.create_sessions(num_sessions=3, headless=headless, ms_tokens=ms_tokens)

    try:
        # Kill first session
        await api.sessions[0].page.close()
        await api.sessions[0].context.close()
        api.sessions[0].is_valid = False

        initial_count = len(api.sessions)
        assert initial_count == 3

        # Run recovery
        await api._recover_sessions()

        # Should have removed the dead session
        assert len(api.sessions) == 2, "Should have removed 1 dead session"

        # All remaining sessions should be valid
        for session in api.sessions:
            assert await api._is_session_valid(session)

    finally:
        await api.close_sessions()
        await api.stop_playwright()


@pytest.mark.asyncio
async def test_session_recovery_disabled(headless, ms_token):
    """Test that recovery can be disabled"""
    api = TikTokApi()
    ms_tokens = [ms_token] if ms_token else None
    await api.create_sessions(
        num_sessions=2,
        headless=headless,
        ms_tokens=ms_tokens,
        enable_session_recovery=False,
    )

    try:
        # Recovery should be disabled
        assert not api._session_recovery_enabled

        # Kill all sessions
        for session in api.sessions:
            await session.page.close()
            await session.context.close()
            session.is_valid = False

        # get_valid_session should fail when all sessions are dead
        with pytest.raises(Exception, match="No valid sessions available"):
            await api._get_valid_session_index()

    finally:
        await api.close_sessions()
        await api.stop_playwright()


@pytest.mark.asyncio
async def test_close_sessions_graceful_with_dead_sessions(headless, ms_token):
    """Test that close_sessions handles already-closed sessions gracefully"""
    api = TikTokApi()
    ms_tokens = [ms_token] if ms_token else None
    await api.create_sessions(num_sessions=2, headless=headless, ms_tokens=ms_tokens)

    # Kill one session manually before closing
    await api.sessions[0].page.close()
    await api.sessions[0].context.close()

    # This should not raise an exception
    await api.close_sessions()
    await api.stop_playwright()

    # All sessions should be cleared
    assert len(api.sessions) == 0


@pytest.mark.asyncio
async def test_specific_session_index_validation(headless, ms_token):
    """Test requesting a specific session index with validation"""
    api = TikTokApi()
    ms_tokens = [ms_token] if ms_token else None
    await api.create_sessions(num_sessions=3, headless=headless, ms_tokens=ms_tokens)

    try:
        # Request specific valid session
        idx, session = await api._get_valid_session_index(session_index=1)
        assert idx == 1
        assert session == api.sessions[1]

        # Save reference to the session we're about to kill
        dead_session_ref = api.sessions[1]

        # Kill that specific session - mark_invalid will auto-remove it from the list
        await api._mark_session_invalid(dead_session_ref)

        # Now sessions list has changed - session 1 is gone, only 0 and 2 remain
        assert len(api.sessions) == 2, "Dead session should be auto-removed"
        assert (
            dead_session_ref not in api.sessions
        ), "Dead session should not be in list"

        # Requesting with session_index=1 now should get one of the remaining valid sessions
        # (since the specific session doesn't exist anymore, recovery finds another)
        idx2, session2 = await api._get_valid_session_index(session_index=1)

        # Should get a valid session (not the dead one)
        assert session2.is_valid, "Should get a valid session"
        assert session2 in api.sessions, "Should get a session from the current list"

    finally:
        await api.close_sessions()
        await api.stop_playwright()


@pytest.mark.asyncio
async def test_backwards_compatibility(headless, ms_token):
    """Test that old _get_session method still works"""
    api = TikTokApi()
    ms_tokens = [ms_token] if ms_token else None
    await api.create_sessions(num_sessions=2, headless=headless, ms_tokens=ms_tokens)

    try:
        # Old method should still work
        idx, session = api._get_session()
        assert idx is not None
        assert session is not None
        assert session in api.sessions

        # With specific index
        idx, session = api._get_session(session_index=0)
        assert idx == 0
        assert session == api.sessions[0]

    finally:
        await api.close_sessions()
        await api.stop_playwright()


@pytest.mark.asyncio
@pytest.mark.skip(reason="Integration test - requires network")
async def test_real_request_with_session_failure(headless, ms_token):
    """Integration test: Make real request and handle session failure"""
    api = TikTokApi()
    ms_tokens = [ms_token] if ms_token else None
    await api.create_sessions(num_sessions=3, headless=headless, ms_tokens=ms_tokens)

    try:
        # Make a real request (should work)
        trending = api.trending()
        videos = await trending.videos(count=5)
        assert len(videos) > 0

        # Kill a session
        await api.sessions[0].page.close()
        await api.sessions[0].context.close()

        # Should still work with remaining sessions
        videos = await trending.videos(count=5)
        assert len(videos) > 0

    finally:
        await api.close_sessions()
        await api.stop_playwright()


@pytest.mark.asyncio
async def test_concurrent_session_access(headless, ms_token):
    """Test that concurrent access to sessions is handled safely"""
    api = TikTokApi()
    ms_tokens = [ms_token] if ms_token else None
    await api.create_sessions(num_sessions=3, headless=headless, ms_tokens=ms_tokens)

    try:
        # Multiple coroutines trying to get sessions concurrently
        async def get_session_task():
            idx, session = await api._get_valid_session_index()
            await asyncio.sleep(0.1)  # Simulate some work
            return await api._is_session_valid(session)

        # Run 10 concurrent tasks
        results = await asyncio.gather(*[get_session_task() for _ in range(10)])

        # All should succeed
        assert all(results), "All concurrent session requests should succeed"

    finally:
        await api.close_sessions()
        await api.stop_playwright()


@pytest.mark.asyncio
async def test_session_recovery_with_lock(headless, ms_token):
    """Test that session recovery uses locking to prevent race conditions"""
    api = TikTokApi()
    ms_tokens = [ms_token] if ms_token else None
    await api.create_sessions(num_sessions=1, headless=headless, ms_tokens=ms_tokens)

    try:
        # Kill the session and mark as invalid
        await api.sessions[0].page.close()
        await api.sessions[0].context.close()
        api.sessions[0].is_valid = (
            False  # Mark as invalid so recovery knows to remove it
        )

        # Multiple concurrent recovery attempts
        async def recovery_task():
            await api._recover_sessions()

        # Should not raise any errors due to race conditions
        await asyncio.gather(*[recovery_task() for _ in range(5)])

        # Session should be cleaned up
        assert len(api.sessions) == 0, f"Expected 0 sessions, got {len(api.sessions)}"

    finally:
        await api.close_sessions()
        await api.stop_playwright()
