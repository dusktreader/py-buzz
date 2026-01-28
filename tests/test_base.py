from __future__ import annotations

from types import TracebackType

import pytest

from buzz.base import Buzz
from buzz.tools import ExcBuilderParams


def test_Buzz_require_condition__basic():
    Buzz.require_condition(True, "should not fail")
    with pytest.raises(Buzz, match="fail message") as err_info:
        Buzz.require_condition(False, "fail message")
    assert err_info.value.base_message is None


def test_Buzz_enforce_defined__basic():
    Buzz.enforce_defined("dummy", "should not fail")
    with pytest.raises(Buzz, match="fail message"):
        Buzz.enforce_defined(None, "fail message")


def test_Buzz_ensure_type__basic():
    val: str | int = "dummy"
    Buzz.ensure_type(val, str, "should not fail")
    with pytest.raises(Buzz, match="fail message"):
        val = 13
        Buzz.ensure_type(val, str, "fail message")


def test_Buzz_handle_errors__basic():
    with pytest.raises(Buzz) as err_info:
        with Buzz.handle_errors("intercepted exception"):
            raise ValueError("there was a problem")

    assert "there was a problem" in str(err_info.value)
    assert "intercepted exception" in str(err_info.value)
    assert "ValueError" in str(err_info.value)
    assert err_info.value.base_message == "intercepted exception"


def test_Buzz_handle_errors__false_re_raise_absorbs_errors():
    with Buzz.handle_errors("intercepted exception", re_raise=False):
        pass


def test_Buzz_check_expressions__basic():
    with pytest.raises(Buzz) as err_info:
        with Buzz.check_expressions("there will be errors") as check:
            check(True)
            check(False)
            check(1 == 2, "one is not two")  # pyright: ignore[reportUnnecessaryComparison]
            check("cooooooool", "not a problem")
            check(0, "zero is still zero")
    err_msg = err_info.value.message
    assert "there will be errors" in err_msg
    assert "1st expression failed" not in err_msg
    assert "2nd expression failed" in err_msg
    assert "one is not two" in err_msg
    assert "not a problem" not in err_msg
    assert "zero is still zero" in err_msg
    assert err_info.value.base_message == "there will be errors"


def test_Buzz__repr():
    """Ensure repr returns class name for better debugging."""
    err = Buzz("Some error message")
    assert repr(err) == "Buzz"

    # Also test with derived class
    class CustomBuzz(Buzz):
        pass

    custom_err = CustomBuzz("Custom error")
    assert repr(custom_err) == "CustomBuzz"


def test_Buzz_exc_builder__raises_on_mismatched_class():
    """Ensure exc_builder validates the exception class matches."""

    class OtherBuzz(Buzz):
        pass

    params = ExcBuilderParams(
        raise_exc_class=OtherBuzz,
        message="test",
        raise_args=[],
        raise_kwargs={},
    )

    with pytest.raises(RuntimeError, match="non-matching `raise_exc_class`"):
        Buzz.exc_builder(params)


def test_Buzz_get_traceback():
    """Verify get_traceback can be called via Buzz class."""
    try:
        raise ValueError("test error")
    except ValueError:
        tb = Buzz.get_traceback()
        assert tb is not None
        assert isinstance(tb, TracebackType)


def test_Buzz_retry__basic():
    """Test Buzz.retry decorator works."""
    call_count = 0

    @Buzz.retry("Operation failed after {attempts} attempts", max_attempts=3, backoff=0.01, jitter=False)
    def flaky_func():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ConnectionError("Failed")
        return "success"

    result = flaky_func()
    assert result == "success"
    assert call_count == 2


def test_Buzz_retry__raises_buzz_on_failure():
    """Test that Buzz.retry raises Buzz exception on final failure."""

    @Buzz.retry("Operation failed after {attempts} attempts", max_attempts=2, backoff=0.01, jitter=False)
    def always_fails():
        raise ConnectionError("Network error")

    with pytest.raises(Buzz) as err_info:
        always_fails()

    assert "Operation failed after 2 attempts" in str(err_info.value)
    assert "Network error" in str(err_info.value)


@pytest.mark.asyncio
async def test_Buzz_retry_async__basic():
    """Test Buzz.retry_async decorator works."""
    call_count = 0

    @Buzz.retry_async("Operation failed after {attempts} attempts", max_attempts=3, backoff=0.01, jitter=False)
    async def flaky_func():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ConnectionError("Failed")
        return "success"

    result = await flaky_func()
    assert result == "success"
    assert call_count == 2


@pytest.mark.asyncio
async def test_Buzz_retry_async__raises_buzz_on_failure():
    """Test that Buzz.retry_async raises Buzz exception on final failure."""

    @Buzz.retry_async("Operation failed after {attempts} attempts", max_attempts=2, backoff=0.01, jitter=False)
    async def always_fails():
        raise ConnectionError("Network error")

    with pytest.raises(Buzz) as err_info:
        await always_fails()

    assert "Operation failed after 2 attempts" in str(err_info.value)
    assert "Network error" in str(err_info.value)
