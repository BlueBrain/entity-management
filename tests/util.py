# pylint: disable=missing-docstring
import re
import sys

from contextlib import contextmanager

from io import StringIO


@contextmanager
def captured_output():
    """Capture the python streams

    To be used as:
    with captured_output() as (out, err):
        print('hello world')
    assert_equal(out.getvalue().strip(), 'hello world')
    """
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def strip_color_codes(string):
    """Strip color codes from the input string"""
    ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", string)


def strip_all(string):
    """Strip color code and whitespace at the beginning end of each line"""
    return "\n".join(strip_color_codes(line).strip() for line in string.split("\n"))


def assert_substring(substring, string):
    sep = ["\n" + 80 * ">" + "\n", "\n" + 80 * "<" + "\n"]
    assert substring in string == "{}\n NOT IN \n{}".format(substring.join(sep), string.join(sep))
