import traceback

import pytest

from buzz.base import Buzz


class MiraNova(Buzz):
    def __init__(self, message, extra_arg, extra_kwarg=None):
        self.extra_arg = extra_arg
        self.extra_kwarg = extra_kwarg
        super().__init__(message)


class WarpDarkmatter(Buzz):
    def __init__(self, extra_arg, detail="", extra_kwarg=None):
        self.extra_arg = extra_arg
        self.extra_kwarg = extra_kwarg
        self.detail = detail


def warp_builder(exc, message, *args, **kwargs):
    return exc(*args, detail=message, **kwargs)



def test_derived_require_condition():
    with pytest.raises(MiraNova, match="fail message") as err_info:
        MiraNova.require_condition(
            False,
            "fail message",
            raise_args=["extra arg"],
            raise_kwargs=dict(extra_kwarg="extra kwarg"),
        )

    assert err_info.value.extra_arg == "extra arg"
    assert err_info.value.extra_kwarg == "extra kwarg"

    with pytest.raises(WarpDarkmatter) as err_info:
        WarpDarkmatter.require_condition(
            False,
            "fail message",
            raise_args=["extra arg"],
            raise_kwargs=dict(extra_kwarg="extra kwarg"),
            exc_builder=warp_builder,
        )

    assert err_info.value.extra_arg == "extra arg"
    assert err_info.value.extra_kwarg == "extra kwarg"
    assert err_info.value.detail == "fail message"


def test_derived_check_expressions():
    with pytest.raises(MiraNova) as err_info:
        with MiraNova.check_expressions(
            "there will be errors",
            raise_args=["extra arg"],
            raise_kwargs=dict(extra_kwarg="extra kwarg"),
        ) as check:
            check(True)
            check(False)
            check(1 == 2, "one is not two")
            check("cooooooool", "not a problem")
            check(0, "zero is still zero")
    err_msg = err_info.value.message
    assert "there will be errors" in err_msg
    assert "1st expression failed" not in err_msg
    assert "2nd expression failed" in err_msg
    assert "one is not two" in err_msg
    assert "not a problem" not in err_msg
    assert "zero is still zero" in err_msg

    assert err_info.value.extra_arg == "extra arg"
    assert err_info.value.extra_kwarg == "extra kwarg"

    with pytest.raises(WarpDarkmatter) as err_info:
        with WarpDarkmatter.check_expressions(
            "there will be errors",
            raise_args=["extra arg"],
            raise_kwargs=dict(extra_kwarg="extra kwarg"),
            exc_builder=warp_builder,
        ) as check:
            check(True)
            check(False)
            check(1 == 2, "one is not two")
            check("cooooooool", "not a problem")
            check(0, "zero is still zero")

    assert err_info.value.extra_arg == "extra arg"
    assert err_info.value.extra_kwarg == "extra kwarg"
    assert "there will be errors" in err_info.value.detail
    assert "1st expression failed" not in err_info.value.detail
    assert "2nd expression failed" in err_info.value.detail
    assert "one is not two" in err_info.value.detail
    assert "not a problem" not in err_info.value.detail
    assert "zero is still zero" in err_info.value.detail


def test_derived_handle_errors():
    with pytest.raises(MiraNova) as err_info:
        with MiraNova.handle_errors(
            "intercepted exception",
            raise_args=["extra arg"],
            raise_kwargs=dict(extra_kwarg="extra kwarg"),
        ):
            raise ValueError("there was a problem")
    assert "there was a problem" in str(err_info.value)
    assert "intercepted exception" in str(err_info.value)
    assert "ValueError" in str(err_info.value)

    assert err_info.value.extra_arg == "extra arg"
    assert err_info.value.extra_kwarg == "extra kwarg"

    with pytest.raises(WarpDarkmatter) as err_info:
        with WarpDarkmatter.handle_errors(
            "intercepted exception",
            raise_args=["extra arg"],
            raise_kwargs=dict(extra_kwarg="extra kwarg"),
            exc_builder=warp_builder,
        ):
            raise ValueError("there was a problem")

    assert err_info.value.extra_arg == "extra arg"
    assert err_info.value.extra_kwarg == "extra kwarg"
    assert "there was a problem" in err_info.value.detail
    assert "intercepted exception" in err_info.value.detail
    assert "ValueError" in err_info.value.detail
