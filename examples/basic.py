from buzz import Buzz


class MyException(Buzz):
    pass


if __name__ == '__main__':
    with MyException.handle_errors("something went wrong"):
        print("we are fine")
        raise Exception("here we die")
        print("we should not get here")
