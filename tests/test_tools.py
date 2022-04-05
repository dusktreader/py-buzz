from traceback import format_tb
from types import TracebackType

import pytest


from buzz.tools import (
    require_condition,
    check_expressions,
    handle_errors,
    reformat_exception,
    get_traceback,
    DoExceptParams,
)


class DummyException(Exception):
    pass


class DummyArgsException(Exception):
    def __init__(self, message, dummy_arg, dummy_kwarg=None):
        self.dummy_arg = dummy_arg
        self.dummy_kwarg = dummy_kwarg


def test_require_condition__basic():
    require_condition(True, "should not fail")
    with pytest.raises(Exception, match="fail message"):
        require_condition(False, "fail message")


def test_require_condition__specific_raise_exc_class():
    require_condition(True, "should not fail", raise_exc_class=DummyException)
    with pytest.raises(DummyException, match="fail message"):
        require_condition(False, "fail message", raise_exc_class=DummyException)


def test_require_condition__raises_ValueError_if_raise_exc_class_is_None():
    with pytest.raises(ValueError, match="raise_exc_class kwarg may not be None"):
        require_condition(True, "doesn't matter", raise_exc_class=None)


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


def test_handle_errors__with_do_else():
    check_list = []
    with handle_errors(
        "no errors should happen here, but do_else should be called",
        do_else=lambda: check_list.append(1),
    ):
        pass

    assert check_list == [1]


def test_handle_errors__with_do_finally():
    check_list = []
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
    check_list = []
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
    assert "there was a problem" in problem.final_message
    assert isinstance(problem.err, Exception)
    assert isinstance(problem.trace, TracebackType)

def test_handle_errors__does_not_raise_when_raise_exc_class_is_None():
    check_list = []
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

    class SpecialError2(Exception):
        pass

    with pytest.raises(RuntimeError) as err_info:
        with handle_errors(
            "there was a problem",
            raise_exc_class=DummyException,
            handle_exc_class=SpecialError1,
        ):
            raise RuntimeError("there was a problem")

    with pytest.raises(DummyException) as err_info:
        with handle_errors(
            "there was a problem",
            raise_exc_class=DummyException,
            handle_exc_class=SpecialError1,
        ):
            raise SpecialError1("there was a problem")

    with pytest.raises(DummyException) as err_info:
        with handle_errors(
            "there was a problem",
            raise_exc_class=DummyException,
            handle_exc_class=SpecialError1,
        ):
            raise SpecialError1("there was a problem")


def test_handle_errors__as_decorator_no_exceptions():
    @handle_errors("no errors should happen here")
    def do_stuff(arg, kwarg="default"):
        return f"stuff: arg={arg}, kwarg={kwarg}"

    assert do_stuff("blah", kwarg="barf") == "stuff: arg=blah, kwarg=barf"


def test_errors_handled__as_decorator_basic_handling():
    @handle_errors("intercepted exception")
    def do_stuff(arg, kwarg="default"):
        raise ValueError("there was a problem")

    with pytest.raises(Exception) as err_info:
        do_stuff("blah", kwarg="barf")

    assert "there was a problem" in str(err_info.value)
    assert "intercepted exception" in str(err_info.value)
    assert "ValueError" in str(err_info.value)


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
