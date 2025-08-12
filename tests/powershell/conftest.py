import pytest
import docker
from testcontainers.core.container import DockerContainer


@pytest.fixture
def powershell_container():
    """PowerShell容器fixture，使用sleep確保容器保持運行狀態供exec命令使用"""
    _ensure_docker_is_available()
    
    try:
        with DockerContainer("powershell-image").with_command("sleep 30") as container:
            yield container
    except Exception as container_error:
        error_message: str = str(container_error).lower()
        if _is_image_not_found_error(error_message):
            pytest.fail(_build_image_not_found_error_message(container_error))
        else:
            pytest.fail(f"PowerShell容器啟動失敗: {container_error}")
    except KeyboardInterrupt:
        pytest.skip("測試被用戶中斷")


def _ensure_docker_is_available() -> None:
    """確保Docker可用，否則跳過測試"""
    try:
        docker_client = docker.from_env()
        docker_client.ping()
    except Exception:
        pytest.skip("Docker不可用，跳過容器測試")


def _is_image_not_found_error(error_message: str) -> bool:
    return "not found" in error_message or "no such image" in error_message


def _build_image_not_found_error_message(original_error: Exception) -> str:
    return (
        f"PowerShell容器啟動失敗: {original_error}\n\n"
        "可能的解決方案:\n"
        "1. 建構Docker image: ./scripts/build-powershell-image.sh\n"
        "2. 檢查Docker是否正在運行\n"
        "3. 確認image名稱是否正確: docker images | grep powershell-image\n"
    )