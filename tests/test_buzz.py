import pytest

from buzz import Buzz


class TestBuzz:

    def test_formatting(self):
        with pytest.raises(Buzz) as err_info:
            raise Buzz('fail message with no formatting')
        assert 'fail message with no formatting' in str(err_info.value)

        with pytest.raises(Buzz) as err_info:
            raise Buzz('fail message with {}', 'arg formatting')
        assert 'fail message with arg formatting' in str(err_info.value)

        with pytest.raises(Buzz) as err_info:
            raise Buzz('fail message with {fmt}', fmt='kwarg formatting')
        assert 'fail message with kwarg formatting' in str(err_info.value)

    def test_require_condition(self):
        Buzz.require_condition(True, 'should not fail')
        with pytest.raises(Buzz) as err_info:
            Buzz.require_condition(False, 'fail message with {}', 'formatting')
        assert 'fail message with formatting' in str(err_info.value)

    def test_handle_errors(self):
        with Buzz.handle_errors('no errors should happen here'):
            pass
        with pytest.raises(Buzz) as err_info:
            with Buzz.handle_errors('intercepted exception'):
                raise Exception("there was a problem")
        assert 'there was a problem' in str(err_info.value)
        assert 'intercepted exception' in str(err_info.value)
