from lab8.__main__ import f


def test_f():
    assert f(4) == 12
    assert f(0) == 0
    assert f(-4) == -12
