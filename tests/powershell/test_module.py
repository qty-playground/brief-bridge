import os
import pytest

import brief_bridge


@pytest.mark.container
class TestPowerShellBasicModule:
    
    def test_basic_powershell_functionality(self, powershell_container):
        """Test basic PowerShell functionality in container"""
        container = powershell_container
        
        self._verify_powershell_works(container)
        self._verify_basic_commands(container)
        self._verify_variables_and_objects(container)
    
    def test_file_mounting_and_script_execution(self, powershell_container):
        """Test mounting files and executing PowerShell scripts"""
        project_root = os.path.dirname(os.path.dirname(brief_bridge.__file__))
        
        from testcontainers.core.container import DockerContainer
        
        with (DockerContainer("powershell-image")
              .with_command("sleep 30")
              .with_volume_mapping(project_root, "/host", mode="ro")) as container:
            
            self._verify_mount_accessibility(container)
            self._verify_simple_script_execution(container)
            self._verify_brief_bridge_files_accessible(container)
    
    def _verify_powershell_works(self, container) -> None:
        """Test that PowerShell is working and accessible"""
        basic_test = container.exec("pwsh -c 'Write-Output \"Hello PowerShell\"'")
        assert basic_test.exit_code == 0
        output = basic_test.output.decode('utf-8')
        assert "Hello PowerShell" in output
    
    def _verify_basic_commands(self, container) -> None:
        """Test basic PowerShell commands work"""
        # Test Get-Process command
        process_test = container.exec("pwsh -c 'Get-Process | Select-Object -First 1'")
        assert process_test.exit_code == 0
        
        # Test arithmetic operations
        math_test = container.exec("pwsh -c '2 + 3'")
        assert math_test.exit_code == 0
        output = math_test.output.decode('utf-8').strip()
        assert "5" in output
        
        # Test string operations
        string_test = container.exec("pwsh -c '\"Hello\" + \" \" + \"World\"'")
        assert string_test.exit_code == 0
        output = string_test.output.decode('utf-8')
        assert "Hello World" in output
    
    def _verify_variables_and_objects(self, container) -> None:
        """Test PowerShell variables and object operations"""
        # Test variable assignment and access
        var_test = container.exec("pwsh -c '$name = \"Brief Bridge\"; Write-Output $name'")
        assert var_test.exit_code == 0
        output = var_test.output.decode('utf-8')
        assert "Brief Bridge" in output
        
        # Test object creation and property access
        object_test = container.exec("pwsh -c '$obj = [PSCustomObject]@{Name=\"Test\"; Value=42}; $obj.Name'")
        assert object_test.exit_code == 0
        output = object_test.output.decode('utf-8')
        assert "Test" in output
        
        # Test array operations
        array_test = container.exec("pwsh -c '$arr = @(1,2,3); $arr.Length'")
        assert array_test.exit_code == 0
        output = array_test.output.decode('utf-8').strip()
        assert "3" in output
    
    def _verify_mount_accessibility(self, container) -> None:
        """Test that mounted volume is accessible"""
        # Test that /host directory exists
        mount_test = container.exec("ls -la /host")
        assert mount_test.exit_code == 0
        
        # Test that we can see project files
        files_test = container.exec("ls /host")
        assert files_test.exit_code == 0
        output = files_test.output.decode('utf-8')
        assert "brief_bridge" in output or "setup.py" in output
    
    def _verify_simple_script_execution(self, container) -> None:
        """Test executing PowerShell scripts via mounted files"""
        # Test that the test script exists in mounted volume
        script_check = container.exec("ls -la /host/tests/powershell/test_script.ps1")
        assert script_check.exit_code == 0
        
        # Execute the mounted test script
        execute_script = container.exec("pwsh -File /host/tests/powershell/test_script.ps1")
        assert execute_script.exit_code == 0
        output = execute_script.output.decode('utf-8')
        assert "Hello from Brief Bridge PowerShell Test" in output
        assert "PowerShell Version:" in output
        assert "Sum of numbers 1-5: 15" in output
        
        # Test script with parameters
        param_script = container.exec("pwsh -File /host/tests/powershell/test_script.ps1 -Message 'Custom Test Message'")
        assert param_script.exit_code == 0
        param_output = param_script.output.decode('utf-8')
        assert "Custom Test Message" in param_output
    
    def _verify_brief_bridge_files_accessible(self, container) -> None:
        """Test that Brief Bridge project files are accessible"""
        # Test access to main package directory
        pkg_test = container.exec("ls -la /host/brief_bridge/")
        assert pkg_test.exit_code == 0
        
        # Test reading a Python file via PowerShell
        read_test = container.exec("pwsh -c 'Get-Content /host/setup.py | Select-Object -First 5'")
        assert read_test.exit_code == 0
        output = read_test.output.decode('utf-8')
        assert "setup" in output.lower() or "from" in output or "import" in output