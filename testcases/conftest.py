import pytest


def pytest_html_report_title(report):
    report.title = "测试报告"


@pytest.fixture
def login():
    """登录"""
    print('登录')
