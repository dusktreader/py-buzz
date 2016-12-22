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

        check_list = []
        with Buzz.handle_errors(
            'no errors should happen here, but finally should be called',
            do_finally=lambda: check_list.append(1)
        ):
            pass
        assert check_list == [1]

        check_list = []
        with pytest.raises(Buzz) as err_info:
            with Buzz.handle_errors(
                'intercepted exception',
                do_finally=lambda: check_list.append(1)
            ):
                raise Exception("there was a problem")
        assert 'there was a problem' in str(err_info.value)
        assert 'intercepted exception' in str(err_info.value)
        assert check_list == [1]

        check_list = []
        with Buzz.handle_errors(
            'no errors should happen here, so on_error should not be called',
            on_error=lambda e, m: check_list.append(m),
        ):
            pass
        assert check_list == []

        check_list = []
        with pytest.raises(Buzz) as err_info:
            with Buzz.handle_errors(
                'intercepted exception',
                on_error=lambda e, m: check_list.append(m),
            ):
                raise Exception("there was a problem")
        assert 'there was a problem' in str(err_info.value)
        assert 'intercepted exception' in str(err_info.value)
        assert len(check_list) == 1
        assert 'there was a problem' in check_list[0]

    def test_accumulate_errors(self):
        with pytest.raises(Buzz) as err_info:
            with Buzz.accumulate_errors('there will be errors') as checker:
                checker += True
                checker += False
                checker += 1 == 2
                checker += 'cooooooool'
                checker += 0
        err_msg = err_info.value.message
        assert 'there will be errors' in err_msg
        assert '`checker += True` resolved as false' not in err_msg
        assert '`checker += False` resolved as false' in err_msg
        assert '`checker += 1 == 2` resolved as false' in err_msg
        assert '`checker += \'cooooooool\' resolved as false' not in err_msg
        assert '`checker += 0` resolved as false' in err_msg
