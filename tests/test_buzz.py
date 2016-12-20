import pytest

from buzz import Buzz


class TestBuzz:

    def test_require_condition(self):
        with pytest.raises(Buzz) as err_info:
            Buzz.require_condition(False, 'fail message with {}', 'formatting')
        assert 'fail message with formatting' in str(err_info.value)
