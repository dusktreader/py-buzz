import pytest

from buzz.base import Buzz


def test_Buzz_require_condition__basic():
    Buzz.require_condition(True, "should not fail")
    with pytest.raises(Buzz, match="fail message") as err_info:
        Buzz.require_condition(False, "fail message")
    assert err_info.value.base_message is None


def test_Buzz_enforce_defined__basic():
    Buzz.enforce_defined("dummy", "should not fail")
    with pytest.raises(Buzz, match="fail message"):
        Buzz.enforce_defined(None, "fail message")


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
    assert err_info.value.base_message == "there will be errors"
