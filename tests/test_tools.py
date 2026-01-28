from __future__ import annotations

from traceback import format_tb
from types import TracebackType
from typing import Any, cast

from typing_extensions import override

import pytest

from buzz.tools import (
    DoExceptParams,
    ExcBuilderParams,
    check_expressions,
    enforce_defined,
    ensure_type,
    get_traceback,
    handle_errors,
    handle_errors_async,
    reformat_exception,
    require_condition,
    retry,
    retry_async,
)

# ==== helpers =========================================================================================================


class DummyException(Exception):
    pass


class DummyArgsException(Exception):
    def __init__(self, message: str, dummy_arg: Any, dummy_kwarg: Any | None = None, base_message: str | None = ""):
        super().__init__(message)
        self.dummy_arg: Any = dummy_arg
        self.dummy_kwarg: Any = dummy_kwarg
        self.base_message: str | None = base_message


class DummyWeirdArgsException(Exception):
    def __init__(self, dummy_arg: Any, detail: str = "", dummy_kwarg: Any | None = None, base_message: str | None = ""):
        super().__init__()
        self.dummy_arg: Any = dummy_arg
        self.dummy_kwarg: Any = dummy_kwarg
        self.detail: str = detail
        self.base_message: str | Any = base_message


def alt_builder(params: ExcBuilderParams) -> Exception:
    exc_class = cast(type[DummyWeirdArgsException], params.raise_exc_class)
    kwargs = {
        **params.raise_kwargs,
        "detail": params.message,
        "base_message": params.base_message,
    }
    return exc_class(*params.raise_args, **kwargs)


# ==== require_condition tests =========================================================================================


def test_require_condition__basic():
    require_condition(True, "should not fail")
    with pytest.raises(Exception, match="fail message"):
        require_condition(False, "fail message")


def test_require_condition__specific_raise_exc_class():
    require_condition(True, "should not fail", raise_exc_class=DummyException)
    with pytest.raises(DummyException, match="fail message"):
        require_condition(False, "fail message", raise_exc_class=DummyException)


def test_require_condition__passes_along_raise_args_and_raise_kwargs():
    with pytest.raises(DummyArgsException, match="fail message") as err_info:
        require_condition(
            False,
            "fail message",
            raise_exc_class=DummyArgsException,
            raise_args=["dummy arg"],
            raise_kwargs=dict(dummy_kwarg="dummy kwarg"),
        )

    assert err_info.value.dummy_arg == "dummy arg"
    assert err_info.value.dummy_kwarg == "dummy kwarg"


def test_require_condition__using_alternative_exception_builder():
    with pytest.raises(DummyWeirdArgsException) as err_info:
        require_condition(
            False,
            "fail message",
            raise_exc_class=DummyWeirdArgsException,
            raise_args=["dummy arg"],
            raise_kwargs=dict(dummy_kwarg="dummy kwarg"),
            exc_builder=alt_builder,
        )

    assert err_info.value.dummy_arg == "dummy arg"
    assert err_info.value.detail == "fail message"
    assert err_info.value.dummy_kwarg == "dummy kwarg"


def test_require_condition__with_do_else():
    check_list: list[int] = []
    require_condition(True, "should not fail", do_else=lambda: check_list.append(1))
    assert check_list == [1]


def test_require_condition__with_do_except():
    check_list: list[Exception] = []
    with pytest.raises(Exception, match="fail message"):
        require_condition(False, "fail message", do_except=lambda e: check_list.append(e))
    assert len(check_list) == 1
    assert "fail message" in str(check_list[0])


# ==== enforce_defined tests ===========================================================================================


def test_enforce_defined__basic():
    some_val: str | None = "boo"
    some_val = enforce_defined(some_val, "should not fail")
    with pytest.raises(Exception, match="fail message"):
        some_val = None
        enforce_defined(some_val, "fail message")


def test_enforce_defined__specific_raise_exc_class():
    some_val: str | None = "boo"
    some_val = enforce_defined(
        some_val,
        "should not fail",
        raise_exc_class=DummyArgsException,
        raise_args=["dummy arg"],
        raise_kwargs=dict(dummy_kwarg="dummy_kwarg"),
    )

    with pytest.raises(DummyArgsException, match="fail message") as err_info:
        some_val = None
        enforce_defined(
            some_val,
            "fail message",
            raise_exc_class=DummyArgsException,
            raise_args=["dummy arg"],
            raise_kwargs=dict(dummy_kwarg="dummy kwarg"),
        )

    assert err_info.value.dummy_arg == "dummy arg"
    assert err_info.value.dummy_kwarg == "dummy kwarg"


def test_enforce_defined__using_alternative_exception_builder():
    with pytest.raises(DummyWeirdArgsException) as err_info:
        some_val = None
        enforce_defined(
            some_val,
            "fail message",
            raise_exc_class=DummyWeirdArgsException,
            raise_args=["dummy arg"],
            raise_kwargs=dict(dummy_kwarg="dummy kwarg"),
            exc_builder=alt_builder,
        )

    assert err_info.value.dummy_arg == "dummy arg"
    assert err_info.value.dummy_kwarg == "dummy kwarg"
    assert err_info.value.detail == "fail message"


def test_enforce_defined__with_do_else():
    check_list: list[int] = []
    some_val: str | None = "boo"
    some_val = enforce_defined(some_val, "should not fail", do_else=lambda: check_list.append(1))
    assert check_list == [1]


def test_enforce_defined__with_do_except():
    check_list: list[Exception] = []
    some_val = None
    with pytest.raises(Exception, match="fail message"):
        enforce_defined(some_val, "fail message", do_except=lambda e: check_list.append(e))
    assert len(check_list) == 1
    assert "fail message" in str(check_list[0])


# ==== ensure_type tests ===============================================================================================


def test_ensure_type__basic():
    some_val: str | int = "boo"
    some_val = ensure_type(some_val, str, "should not fail")
    assert isinstance(some_val, str)

    with pytest.raises(Exception, match="fail message"):
        some_val = 13
        ensure_type(some_val, str, "fail message")


def test_ensure_type__specific_raise_exc_class():
    some_val: str | int = "boo"
    some_val = ensure_type(
        some_val,
        str,
        "should not fail",
        raise_exc_class=DummyArgsException,
        raise_args=["dummy arg"],
        raise_kwargs=dict(dummy_kwarg="dummy_kwarg"),
    )

    with pytest.raises(DummyArgsException, match="fail message") as err_info:
        some_val = 13
        ensure_type(
            some_val,
            str,
            "fail message",
            raise_exc_class=DummyArgsException,
            raise_args=["dummy arg"],
            raise_kwargs=dict(dummy_kwarg="dummy kwarg"),
        )

    assert err_info.value.dummy_arg == "dummy arg"
    assert err_info.value.dummy_kwarg == "dummy kwarg"


def test_ensure_type__using_alternative_exception_builder():
    with pytest.raises(DummyWeirdArgsException) as err_info:
        some_val: str | int = 13
        ensure_type(
            some_val,
            str,
            "fail message",
            raise_exc_class=DummyWeirdArgsException,
            raise_args=["dummy arg"],
            raise_kwargs=dict(dummy_kwarg="dummy kwarg"),
            exc_builder=alt_builder,
        )

    assert err_info.value.dummy_arg == "dummy arg"
    assert err_info.value.dummy_kwarg == "dummy kwarg"
    assert err_info.value.detail == "fail message"


def test_ensure_type__with_do_else():
    check_list: list[int] = []
    some_val: str | int = "boo"
    some_val = ensure_type(some_val, str, "should not fail", do_else=lambda: check_list.append(1))
    assert check_list == [1]


def test_ensure_type__with_do_except():
    check_list: list[Exception] = []
    some_val: str | int = 13
    with pytest.raises(Exception, match="fail message"):
        ensure_type(some_val, str, "fail message", do_except=lambda e: check_list.append(e))
    assert len(check_list) == 1
    assert "fail message" in str(check_list[0])


def test_ensure_type__uses_default_message():
    """Verify default message formatting includes type name."""
    with pytest.raises(Exception, match="Value was not of type <class 'str'>"):
        ensure_type(42, str)  # No message provided


# ==== handle_errors tests =============================================================================================


def test_handle_errors__no_exceptions():
    with handle_errors("no errors should happen here"):
        pass


def test_handle_errors__basic_handling():
    original_error = ValueError("there was a problem")
    with pytest.raises(Exception) as err_info:
        with handle_errors("intercepted exception"):
            raise original_error

    assert "there was a problem" in str(err_info.value)
    assert "intercepted exception" in str(err_info.value)
    assert "ValueError" in str(err_info.value)
    assert err_info.value.__cause__ is original_error


def test_handle_errors__raise_specific_exception_type():
    with pytest.raises(DummyException) as err_info:
        with handle_errors("intercepted exception", raise_exc_class=DummyException):
            raise ValueError("there was a problem")

    assert "there was a problem" in str(err_info.value)
    assert "intercepted exception" in str(err_info.value)
    assert "ValueError" in str(err_info.value)


def test_handle_errors__uses_raise_args_and_kwargs():
    with pytest.raises(DummyArgsException) as err_info:
        with handle_errors(
            "intercepted exception",
            raise_exc_class=DummyArgsException,
            raise_args=["dummy arg"],
            raise_kwargs=dict(dummy_kwarg="dummy kwarg"),
        ):
            raise ValueError("there was a problem")

    assert "there was a problem" in str(err_info.value)
    assert "intercepted exception" in str(err_info.value)
    assert "ValueError" in str(err_info.value)

    assert err_info.value.dummy_arg == "dummy arg"
    assert err_info.value.dummy_kwarg == "dummy kwarg"


def test_handle_errors____using_alternative_exception_builder():
    with pytest.raises(DummyWeirdArgsException) as err_info:
        with handle_errors(
            "intercepted exception",
            raise_exc_class=DummyWeirdArgsException,
            raise_args=["dummy arg"],
            raise_kwargs=dict(dummy_kwarg="dummy kwarg"),
            exc_builder=alt_builder,
        ):
            raise ValueError("there was a problem")

    assert err_info.value.dummy_arg == "dummy arg"
    assert err_info.value.dummy_kwarg == "dummy kwarg"
    assert "there was a problem" in err_info.value.detail
    assert "intercepted exception" in err_info.value.detail
    assert err_info.value.base_message == "intercepted exception"


def test_handle_errors__with_do_else():
    check_list: list[int] = []
    with handle_errors(
        "no errors should happen here, but do_else should be called",
        do_else=lambda: check_list.append(1),
    ):
        pass

    assert check_list == [1]


def test_handle_errors__with_do_finally():
    check_list: list[int] = []
    with handle_errors(
        "no errors should happen here, but do_finally should be called",
        do_finally=lambda: check_list.append(1),
    ):
        pass

    assert check_list == [1]

    check_list = []
    with pytest.raises(Exception, match="intercepted exception.*there was a problem") as err_info:
        with handle_errors("intercepted exception", do_finally=lambda: check_list.append(1)):
            raise Exception("there was a problem")

    assert "there was a problem" in str(err_info.value)
    assert "intercepted exception" in str(err_info.value)
    assert check_list == [1]


def test_handle_errors__with_do_except():
    check_list: list[DoExceptParams] = []
    with handle_errors(
        "no errors should happen here, so do_except should not be called",
        do_except=lambda p: check_list.append(p),
    ):
        pass
    assert check_list == []

    check_list = []
    with pytest.raises(Exception, match="intercepted exception.*there was a problem") as err_info:
        with handle_errors(
            "intercepted exception",
            do_except=lambda p: check_list.append(p),
        ):
            raise Exception("there was a problem")

    assert "there was a problem" in str(err_info.value)
    assert "intercepted exception" in str(err_info.value)

    (problem, *remains) = check_list
    assert remains == []
    assert "intercepted exception" == problem.base_message
    assert "there was a problem" in problem.final_message
    assert isinstance(problem.err, Exception)
    assert isinstance(problem.trace, TracebackType)


def test_handle_errors__does_not_raise_when_raise_exc_class_is_None():
    check_list: list[DoExceptParams] = []
    with handle_errors(
        "intercepted exception",
        raise_exc_class=None,
        do_except=lambda p: check_list.append(p),
    ):
        raise Exception("there was a problem")

    (problem, *remains) = check_list  # pyright: ignore[reportUnreachable]
    assert remains == []
    assert "there was a problem" in problem.final_message
    assert isinstance(problem.err, Exception)
    assert isinstance(problem.trace, TracebackType)


def test_handle_errors__only_catches_exceptions_matching_handle_exc_class():
    class SpecialError1(Exception):
        pass

    with pytest.raises(RuntimeError):
        with handle_errors(
            "there was a problem",
            raise_exc_class=DummyException,
            handle_exc_class=SpecialError1,
        ):
            raise RuntimeError("there was a problem")

    with pytest.raises(DummyException):
        with handle_errors(
            "there was a problem",
            raise_exc_class=DummyException,
            handle_exc_class=SpecialError1,
        ):
            raise SpecialError1("there was a problem")

    with pytest.raises(DummyException):
        with handle_errors(
            "there was a problem",
            raise_exc_class=DummyException,
            handle_exc_class=SpecialError1,
        ):
            raise SpecialError1("there was a problem")


def test_handle_errors__as_decorator_no_exceptions():
    @handle_errors("no errors should happen here")
    def do_stuff(arg: str, kwarg: str = "default"):
        return f"stuff: arg={arg}, kwarg={kwarg}"

    assert do_stuff("blah", kwarg="barf") == "stuff: arg=blah, kwarg=barf"


def test_handle_errors__as_decorator_basic_handling():
    @handle_errors("intercepted exception")
    def do_stuff(arg: str, kwarg: str = "default"):
        raise ValueError(f"there was a problem: {arg=}, {kwarg=}")

    with pytest.raises(Exception) as err_info:
        do_stuff("blah", kwarg="barf")

    assert "there was a problem" in str(err_info.value)
    assert "intercepted exception" in str(err_info.value)
    assert "ValueError" in str(err_info.value)


def test_handle_errors__ignores_errors_matching_ignore_exc_class():
    with pytest.raises(RuntimeError):
        with handle_errors(
            "there was a problem",
            raise_exc_class=DummyException,
            handle_exc_class=Exception,
            ignore_exc_class=RuntimeError,
        ):
            raise RuntimeError("Boom!")


def test_handle_errors__handles_exception_formatting_failure():
    """Ensure handle_errors is robust if exception string formatting fails."""

    class BadException(Exception):
        @override
        def __str__(self):
            raise RuntimeError("Cannot format this exception")

    with pytest.raises(RuntimeError, match="Failed while formatting message"):
        with handle_errors("base message"):
            raise BadException("original message")


# ==== handle_errors_async tests =======================================================================================


@pytest.mark.asyncio
async def test_handle_errors_async__with_do_else():
    async def _anoop():
        pass

    check_list: list[int] = []

    async def _add_to_list():
        check_list.append(1)

    async with handle_errors_async(
        "no errors should happen here, but do_else should be called",
        do_else=_add_to_list,
    ):
        await _anoop()

    assert check_list == [1]


@pytest.mark.asyncio
async def test_handle_errors_async__with_do_finally():
    async def _anoop():
        pass

    check_list: list[int] = []

    async def _add_to_list():
        check_list.append(1)

    async with handle_errors_async(
        "no errors should happen here, but do_finally should be called",
        do_finally=_add_to_list,
    ):
        await _anoop()

    assert check_list == [1]

    check_list = []
    with pytest.raises(Exception, match="intercepted exception.*there was a problem") as err_info:
        async with handle_errors_async("intercepted exception", do_finally=_add_to_list):
            raise Exception("there was a problem")

    assert "there was a problem" in str(err_info.value)
    assert "intercepted exception" in str(err_info.value)
    assert check_list == [1]


@pytest.mark.asyncio
async def test_handle_errors_async__with_do_except():
    async def _anoop():
        pass

    check_list: list[DoExceptParams] = []

    async def _add_to_list(p: DoExceptParams):
        check_list.append(p)

    async with handle_errors_async(
        "no errors should happen here, so do_except should not be called",
        do_except=_add_to_list,
    ):
        await _anoop()
    assert check_list == []

    check_list = []
    with pytest.raises(Exception, match="intercepted exception.*there was a problem") as err_info:
        async with handle_errors_async(
            "intercepted exception",
            do_except=_add_to_list,
        ):
            raise Exception("there was a problem")

    assert "there was a problem" in str(err_info.value)
    assert "intercepted exception" in str(err_info.value)

    (problem, *remains) = check_list
    assert remains == []
    assert "intercepted exception" == problem.base_message
    assert "there was a problem" in problem.final_message
    assert isinstance(problem.err, Exception)
    assert isinstance(problem.trace, TracebackType)


@pytest.mark.asyncio
async def test_handle_errors_async__with_async_do_except():
    """Test async exception handler with async do_except callback."""
    calls: list[tuple[str, Exception]] = []

    async def async_do_except(params: DoExceptParams):
        calls.append(("except", params.err))

    with pytest.raises(Exception):
        async with handle_errors_async("base message", do_except=async_do_except):
            raise ValueError("test error")

    assert len(calls) == 1
    assert calls[0][0] == "except"
    assert isinstance(calls[0][1], ValueError)


@pytest.mark.asyncio
async def test_handle_errors_async__with_async_do_else():
    """Test async exception handler with async do_else callback."""
    calls: list[str] = []

    async def async_do_else():
        calls.append("else")

    async with handle_errors_async("base message", do_else=async_do_else):
        pass  # No exception

    assert calls == ["else"]


@pytest.mark.asyncio
async def test_handle_errors_async__with_async_do_finally():
    """Test async exception handler with async do_finally callback."""
    calls: list[str] = []

    async def async_do_finally():
        calls.append("finally")

    async with handle_errors_async(
        "base message",
        do_finally=async_do_finally,
        raise_exc_class=None,
    ):
        pass

    assert calls == ["finally"]


@pytest.mark.asyncio
async def test_handle_errors_async__with_sync_callbacks():
    """Test async exception handler with sync (non-async) callbacks."""
    calls: list[str] = []

    def sync_do_except(_params: DoExceptParams):
        calls.append("except")

    def sync_do_else():
        calls.append("else")

    def sync_do_finally():
        calls.append("finally")

    # Test sync do_else
    async with handle_errors_async(
        "base message",
        do_else=sync_do_else,
        raise_exc_class=None,
    ):
        pass

    assert "else" in calls

    # Test sync do_except and do_finally
    calls.clear()
    async with handle_errors_async(
        "base message",
        do_except=sync_do_except,
        do_finally=sync_do_finally,
        raise_exc_class=None,
    ):
        raise ValueError("test error")

    assert "except" in calls  # pyright: ignore[reportUnreachable]
    assert "finally" in calls


@pytest.mark.asyncio
async def test_handle_errors_async__handles_exception_formatting_failure():
    """Ensure async handler is robust if exception string formatting fails."""

    class BadException(Exception):
        @override
        def __str__(self):
            raise RuntimeError("Cannot format this exception")

    with pytest.raises(RuntimeError, match="Failed while formatting message"):
        async with handle_errors_async("base message"):
            raise BadException("original message")


@pytest.mark.asyncio
async def test_handle_errors_async__ignores_errors_matching_ignore_exc_class():
    """Test that async handler re-raises ignored exceptions."""
    with pytest.raises(RuntimeError):
        async with handle_errors_async(
            "there was a problem",
            raise_exc_class=DummyException,
            handle_exc_class=Exception,
            ignore_exc_class=RuntimeError,
        ):
            raise RuntimeError("Boom!")


# ==== check_expressions tests =========================================================================================


def test_check_expressions__basic():
    with pytest.raises(Exception) as err_info:
        with check_expressions("there will be errors") as check:
            check(True)
            check(False)
            check(1 == 2, "one is not two")  # pyright: ignore[reportUnnecessaryComparison]
            check("cooooooool", "not a problem")
            check(0, "zero is still zero")

    err_msg = str(err_info.value)
    assert "there will be errors" in err_msg
    assert "1st expression failed" not in err_msg
    assert "2nd expression failed" in err_msg
    assert "one is not two" in err_msg
    assert "not a problem" not in err_msg
    assert "zero is still zero" in err_msg


def test_check_expressions__raise_specific_exception_type():
    with pytest.raises(DummyException) as err_info:
        with check_expressions("there will be errors", raise_exc_class=DummyException) as check:
            check(False)

    err_msg = str(err_info.value)
    assert "there will be errors" in err_msg
    assert "1st expression failed" in err_msg


def test_check_expressions__uses_raise_args_and_kwargs():
    with pytest.raises(DummyArgsException) as err_info:
        with check_expressions(
            "there will be errors",
            raise_exc_class=DummyArgsException,
            raise_args=["dummy arg"],
            raise_kwargs=dict(dummy_kwarg="dummy kwarg"),
        ) as check:
            check(False)

    err_msg = str(err_info.value)
    assert "there will be errors" in err_msg
    assert "1st expression failed" in err_msg

    assert err_info.value.dummy_arg == "dummy arg"
    assert err_info.value.dummy_kwarg == "dummy kwarg"


def test_check_expressions____using_alternative_exception_builder():
    with pytest.raises(DummyWeirdArgsException) as err_info:
        with check_expressions(
            "there will be errors",
            raise_exc_class=DummyWeirdArgsException,
            raise_args=["dummy arg"],
            raise_kwargs=dict(dummy_kwarg="dummy kwarg"),
            exc_builder=alt_builder,
        ) as check:
            check(False)

    assert err_info.value.dummy_arg == "dummy arg"
    assert err_info.value.dummy_kwarg == "dummy kwarg"
    assert "there will be errors" in err_info.value.detail
    assert "1st expression failed" in err_info.value.detail
    assert err_info.value.base_message == "there will be errors"


def test_check_expressions__with_do_else():
    check_list: list[int] = []
    with check_expressions("there will be errors", do_else=lambda: check_list.append(1)) as check:
        check(True)
    assert check_list == [1]


def test_check_expressions__with_do_except():
    check_list: list[Exception] = []
    with pytest.raises(Exception, match="there will be errors"):
        with check_expressions("there will be errors", do_except=lambda e: check_list.append(e)) as check:
            check(False)
    assert len(check_list) == 1
    assert "there will be errors" in str(check_list[0])


def test_check_expressions__ordinalize_teens():
    """Verify special handling of 11th, 12th, 13th."""
    with pytest.raises(Exception) as err_info:
        with check_expressions("teen ordinals") as check:
            for _ in range(10):
                check(True)  # Fill up to 10
            check(False)  # 11th
            check(False)  # 12th
            check(False)  # 13th

    err_msg = str(err_info.value)
    assert "11th expression failed" in err_msg
    assert "12th expression failed" in err_msg
    assert "13th expression failed" in err_msg


# ==== retry tests =========================================================================================================


def test_retry__succeeds_on_first_attempt():
    """Test that retry doesn't interfere when function succeeds immediately."""
    call_count = 0

    @retry("Operation failed after {attempts} attempts", max_attempts=3)
    def successful_func():
        nonlocal call_count
        call_count += 1
        return "success"

    result = successful_func()
    assert result == "success"
    assert call_count == 1


def test_retry__succeeds_after_retries():
    """Test that retry keeps trying until function succeeds."""
    call_count = 0

    @retry("Operation failed after {attempts} attempts", max_attempts=3, backoff=0.01, jitter=False)
    def flaky_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("Failed")
        return "success"

    result = flaky_func()
    assert result == "success"
    assert call_count == 3


def test_retry__raises_after_max_attempts():
    """Test that retry raises exception after exhausting all attempts."""
    call_count = 0

    @retry("Failed after {attempts} tries", max_attempts=3, backoff=0.01, jitter=False)
    def always_fails():
        nonlocal call_count
        call_count += 1
        raise ConnectionError("Network error")

    with pytest.raises(Exception) as err_info:
        always_fails()

    assert call_count == 3
    assert "Failed after 3 tries" in str(err_info.value)
    assert "Network error" in str(err_info.value)


def test_retry__only_retries_specified_exceptions():
    """Test that retry only catches specified exception types."""
    call_count = 0

    @retry(
        "Operation failed after {attempts} attempts",
        max_attempts=3,
        backoff=0.01,
        retry_on=(ConnectionError, TimeoutError),
    )
    def raises_value_error():
        nonlocal call_count
        call_count += 1
        raise ValueError("Not a connection error")

    with pytest.raises(ValueError, match="Not a connection error"):
        raises_value_error()

    # Should fail immediately, not retry
    assert call_count == 1


def test_retry__with_on_retry_callback():
    """Test that on_retry callback is invoked on each retry."""
    call_count = 0
    retry_attempts: list[tuple[int, str]] = []

    def record_retry(attempt: int, exception: Exception):
        retry_attempts.append((attempt, str(exception)))

    @retry(
        "Operation failed after {attempts} attempts", max_attempts=4, backoff=0.01, jitter=False, on_retry=record_retry
    )
    def flaky_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError(f"Attempt {call_count}")
        return "success"

    result = flaky_func()
    assert result == "success"
    assert call_count == 3
    # on_retry should be called twice (for attempts 1 and 2)
    assert len(retry_attempts) == 2
    assert retry_attempts[0] == (1, "Attempt 1")
    assert retry_attempts[1] == (2, "Attempt 2")


def test_retry__with_custom_exception_class():
    """Test that retry can raise custom exception class."""

    @retry(
        "Operation failed after {attempts} attempts",
        max_attempts=2,
        backoff=0.01,
        jitter=False,
        raise_exc_class=DummyException,
    )
    def always_fails():
        raise ConnectionError("Network error")

    with pytest.raises(DummyException):
        always_fails()


def test_retry__with_raise_args_and_kwargs():
    """Test that retry passes through raise_args and raise_kwargs."""

    @retry(
        "Operation failed after {attempts} attempts",
        max_attempts=2,
        backoff=0.01,
        jitter=False,
        raise_exc_class=DummyArgsException,
        raise_args=["arg_value"],
        raise_kwargs={"dummy_kwarg": "kwarg_value"},
    )
    def always_fails():
        raise ConnectionError("Network error")

    with pytest.raises(DummyArgsException) as err_info:
        always_fails()

    exc = err_info.value
    assert exc.dummy_arg == "arg_value"
    assert exc.dummy_kwarg == "kwarg_value"


def test_retry__validates_max_attempts():
    """Test that retry validates max_attempts >= 1."""
    with pytest.raises(ValueError, match="max_attempts must be at least 1"):
        retry("Operation failed after {attempts} attempts", max_attempts=0)


def test_retry__with_jitter():
    """Test that retry applies jitter when enabled."""
    call_times: list[float] = []

    @retry("Operation failed after {attempts} attempts", max_attempts=3, backoff=1.0, jitter=True, max_delay=1.0)
    def always_fails():
        import time

        call_times.append(time.time())
        raise ConnectionError("Network error")

    with pytest.raises(Exception):
        always_fails()

    # With jitter, delays should be somewhat random but bounded
    assert len(call_times) == 3
    delay1 = call_times[1] - call_times[0]
    delay2 = call_times[2] - call_times[1]
    # Both delays should be between 0 and max_delay (1.0)
    assert 0 <= delay1 <= 1.1  # Allow small timing variance
    assert 0 <= delay2 <= 1.1


def test_retry__exponential_backoff():
    """Test that retry uses exponential backoff (basic timing check)."""
    import time

    call_times: list[float] = []

    @retry("Operation failed after {attempts} attempts", max_attempts=3, backoff=2.0, jitter=False)
    def always_fails():
        call_times.append(time.time())
        raise ConnectionError("Network error")

    with pytest.raises(Exception):
        always_fails()

    # Check that delays are increasing (exponentially)
    # delay = backoff^attempt, so with backoff=2.0: 2^0=1, 2^1=2, 2^2=4
    assert len(call_times) == 3
    delay1 = call_times[1] - call_times[0]
    delay2 = call_times[2] - call_times[1]
    # Delays should be increasing (exponential)
    # delay1 should be ~1 second, delay2 should be ~2 seconds
    assert delay1 >= 0.9  # Allow some timing variance
    assert delay2 >= 1.9
    assert delay2 > delay1


def test_retry__max_delay_cap():
    """Test that retry caps delay at max_delay."""
    call_times: list[float] = []

    @retry("Operation failed after {attempts} attempts", max_attempts=4, backoff=10.0, max_delay=0.05, jitter=False)
    def always_fails():
        import time

        call_times.append(time.time())
        raise ConnectionError("Network error")

    with pytest.raises(Exception):
        always_fails()

    # With backoff=10, delays would be: 10^0=1, 10^1=10, 10^2=100
    # But max_delay=0.05 should cap all delays
    assert len(call_times) == 4
    for i in range(1, len(call_times)):
        delay = call_times[i] - call_times[i - 1]
        # Should be close to max_delay (0.05) but allow some wiggle room
        assert delay < 0.1  # Much less than uncapped delay


@pytest.mark.asyncio
async def test_retry_async__succeeds_on_first_attempt():
    """Test that retry_async doesn't interfere when function succeeds immediately."""
    call_count = 0

    @retry_async("Operation failed after {attempts} attempts", max_attempts=3)
    async def successful_func():
        nonlocal call_count
        call_count += 1
        return "success"

    result = await successful_func()
    assert result == "success"
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_async__succeeds_after_retries():
    """Test that retry_async keeps trying until function succeeds."""
    call_count = 0

    @retry_async("Operation failed after {attempts} attempts", max_attempts=3, backoff=0.01, jitter=False)
    async def flaky_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("Failed")
        return "success"

    result = await flaky_func()
    assert result == "success"
    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_async__raises_after_max_attempts():
    """Test that retry_async raises exception after exhausting all attempts."""
    call_count = 0

    @retry_async("Failed after {attempts} tries", max_attempts=3, backoff=0.01, jitter=False)
    async def always_fails():
        nonlocal call_count
        call_count += 1
        raise ConnectionError("Network error")

    with pytest.raises(Exception) as err_info:
        await always_fails()

    assert call_count == 3
    assert "Failed after 3 tries" in str(err_info.value)
    assert "Network error" in str(err_info.value)


@pytest.mark.asyncio
async def test_retry_async__only_retries_specified_exceptions():
    """Test that retry_async only catches specified exception types."""
    call_count = 0

    @retry_async(
        "Operation failed after {attempts} attempts",
        max_attempts=3,
        backoff=0.01,
        retry_on=(ConnectionError, TimeoutError),
    )
    async def raises_value_error():
        nonlocal call_count
        call_count += 1
        raise ValueError("Not a connection error")

    with pytest.raises(ValueError, match="Not a connection error"):
        await raises_value_error()

    # Should fail immediately, not retry
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_async__with_on_retry_callback():
    """Test that on_retry callback is invoked on each retry in async."""
    call_count = 0
    retry_attempts: list[tuple[int, str]] = []

    def record_retry(attempt: int, exception: Exception):
        retry_attempts.append((attempt, str(exception)))

    @retry_async(
        "Operation failed after {attempts} attempts", max_attempts=4, backoff=0.01, jitter=False, on_retry=record_retry
    )
    async def flaky_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError(f"Attempt {call_count}")
        return "success"

    result = await flaky_func()
    assert result == "success"
    assert call_count == 3
    assert len(retry_attempts) == 2
    assert retry_attempts[0] == (1, "Attempt 1")
    assert retry_attempts[1] == (2, "Attempt 2")


@pytest.mark.asyncio
async def test_retry_async__uses_asyncio_sleep():
    """Test that retry_async uses asyncio.sleep for async compatibility."""
    import time

    call_times: list[float] = []

    @retry_async("Operation failed after {attempts} attempts", max_attempts=3, backoff=0.05, jitter=False)
    async def always_fails():
        call_times.append(time.time())
        raise ConnectionError("Network error")

    with pytest.raises(Exception):
        await always_fails()

    # Verify delays occurred
    assert len(call_times) == 3
    delay1 = call_times[1] - call_times[0]
    # Should have some delay (at least a few milliseconds)
    assert delay1 > 0.01


@pytest.mark.asyncio
async def test_retry_async__validates_max_attempts():
    """Test that retry_async validates max_attempts >= 1."""
    with pytest.raises(ValueError, match="max_attempts must be at least 1"):
        retry_async("Operation failed after {attempts} attempts", max_attempts=0)


# ==== other tests =====================================================================================================


def test_reformat_exception():
    final_message = reformat_exception(
        "I want this to be included",
        Exception("Original Error"),
    )
    assert "I want this to be included" in final_message
    assert "Original Error" in final_message


def test_get_traceback():
    try:
        raise DummyException("Original Error")
    except Exception:
        trace = get_traceback()
    last_frame = format_tb(trace)[-1]
    assert "test_tools.py" in last_frame
    assert "test_get_traceback" in last_frame
    assert 'DummyException("Original Error")' in last_frame
