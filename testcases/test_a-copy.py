import pytest


@pytest.mark.api
@pytest.mark.level(1)
@pytest.mark.owner('韩志超')
def test_a1():
    """测试a1"""
    print('a1')


@pytest.mark.api
def test_a2():
    """测试a2"""
    print('测试a2')


@pytest.mark.owner('韩志超')
@pytest.mark.demo
def test_a3():
    print('a3')
