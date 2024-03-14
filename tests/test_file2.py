from lab8.file2 import *


def test_func2():
    assert func2(3, 4) == 7
    assert func2(3, -3) == 0
    assert func2(0, 0) == 0


def test_split_line():
    '''
    Random comment regarding style guide rules.

    The next lines/tests is more than 80 characters long. Because of that,
    flake8 may get angry and tell you to make it shorter.
    There are multiple way of doing that. The two tests below show you how.
    You can also split some kinds of lines.
    Like
    
    if (x and y and z): ...
    
    can be made into

    if (x and
        y and
        z): ...

    and so on.

    You can also insert other forms of whole-file or specific-file ignores,
    or change or disable rules in the config files.
    '''

    assert split_line('TEL;HOME:+47 123 45 678') == \
        ['TEL;HOME', '+47 123 45 678']


    assert split_line('EMAIL;WORK:paul.knutson@ntnu.no') == ['EMAIL;WORK', 'paul.knutson@ntnu.no']  # noqa: E501
