import traceback

import pytest

from buzz.base import Buzz


class MiraNova(Buzz):
    def __init__(self, message, extra_arg, extra_kwarg=None):
        self.extra_arg = extra_arg
        self.extra_kwarg = extra_kwarg
        super().__init__(message)


class TestDerived:
    def test_require_condition(self):
        with pytest.raises(MiraNova, match="fail message") as err_info:
            MiraNova.require_condition(
                False,
                "fail message",
                "extra arg",
                extra_kwarg="extra kwarg",
            )

        assert err_info.value.extra_arg == "extra arg"
        assert err_info.value.extra_kwarg == "extra kwarg"

    def test_check_expressions(self):
        with pytest.raises(MiraNova) as err_info:
            with MiraNova.check_expressions(
                "extra arg",
                main_message="there will be errors",
                extra_kwarg="extra kwarg",
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

    def test_handle_errors(self):
        with pytest.raises(MiraNova) as err_info:
            with MiraNova.handle_errors(
                "intercepted exception",
                "extra arg",
                extra_kwarg="extra kwarg",
            ):
                raise ValueError("there was a problem")
        assert "there was a problem" in str(err_info.value)
        assert "intercepted exception" in str(err_info.value)
        assert "ValueError" in str(err_info.value)

        assert err_info.value.extra_arg == "extra arg"
        assert err_info.value.extra_kwarg == "extra kwarg"
