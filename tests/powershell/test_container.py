import pytest


@pytest.mark.container
class TestPowerShellContainer:
    
    def test_can_execute_basic_powershell_commands(self, powershell_container):
        execution_result = powershell_container.exec("pwsh -c 'Write-Output \"Hello from PowerShell\"'")
        
        assert execution_result.exit_code == 0
        assert "Hello from PowerShell" in execution_result.output.decode('utf-8')
        
    def test_powershell_version_is_available(self, powershell_container):
        version_result = powershell_container.exec("pwsh --version")
        
        assert version_result.exit_code == 0
        assert "7." in version_result.output.decode('utf-8')