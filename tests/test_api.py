import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """
    创建测试客户端
    """
    with TestClient(app) as c:
        yield c


def test_read_main(client):
    """
    测试主页API
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "微信小程序和公众号后台服务"}


def test_health(client):
    """
    测试健康检查API
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"} 