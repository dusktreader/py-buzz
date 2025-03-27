from __future__ import annotations

from traceback import format_tb
from types import TracebackType
from typing import Any

import pytest


from buzz.tools import (
    require_condition,
    enforce_defined,
    check_expressions,
    handle_errors,
    handle_errors_async,
    reformat_exception,
    get_traceback,
    DoExceptParams,
    ExcBuilderParams,
)


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
    return params.raise_exc_class(
        *params.raise_args,
        detail=params.message,  # pyright: ignore[reportCallIssue]
        base_message=params.base_message,  # pyright: ignore[reportCallIssue]
        **params.raise_kwargs,
    )


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

    (problem, *remains) = check_list
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
    def do_stuff(arg, kwarg="default"):
        raise ValueError("there was a problem")

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


def test_check_expressions__basic():
    with pytest.raises(Exception) as err_info:
        with check_expressions("there will be errors") as check:
            check(True)
            check(False)
            check(1 == 2, "one is not two")
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
