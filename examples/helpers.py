import contextlib
import traceback


@contextlib.contextmanager
def wrap_demo(message):
    """
    Just lets us show the exception from any of the demo methods.
    """
    print("-" * (len(message) + 1))
    print(f"{message}: ")
    print("-" * (len(message) + 1))
    print()
    try:
        yield
    except Exception:
        traceback.print_exc()
    else:
        print("No errors!")
    print()
    print()
