import pytest


@pytest.mark.level(1)
def test_b1():
    print('b1')
@pytest.mark.owner('李磊')
@pytest.mark.level(2)
def test_b2():
    print('b2')


@pytest.mark.level(0)
def test_b3():
    print('b3')