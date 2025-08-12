import os
import pytest

import brief_bridge


@pytest.mark.container
class TestBriefBridgeEditorModule:
    
    def test_module_can_be_mounted_and_executed(self, powershell_container):
        project_root = os.path.dirname(os.path.dirname(brief_bridge.__file__))
        
        from testcontainers.core.container import DockerContainer
        
        with (DockerContainer("powershell-image")
              .with_command("sleep 30")
              .with_volume_mapping(project_root, "/host", mode="ro")) as container:
            
            self._verify_module_files_are_accessible(container)
            self._verify_module_imports_successfully(container)
            self._verify_version_cmdlet_executes(container)
            self._run_regression_tests(container)
            self._run_pester_tests(container)
    
    def _verify_module_files_are_accessible(self, container) -> None:
        module_files = ["BriefBridgeEditor.psd1", "BriefBridgeEditor.psm1", "BriefBridgeEditor.Tests.ps1"]
        
        for filename in module_files:
            file_check = container.exec(f"ls -la /host/{filename}")
            assert file_check.exit_code == 0, f"{filename} not found: {file_check.output.decode()}"
    
    def _verify_module_imports_successfully(self, container) -> None:
        import_test = container.exec(
            "pwsh -c 'Import-Module /host/BriefBridgeEditor.psd1 -Force; Get-BriefBridgeVersion'"
        )
        
        assert import_test.exit_code == 0
        output = import_test.output.decode('utf-8')
        assert "Brief Bridge Editor" in output
        assert "1.0.0" in output
    
    def _verify_version_cmdlet_executes(self, container) -> None:
        version_test = container.exec(
            "pwsh -c 'Import-Module /host/BriefBridgeEditor.psd1 -Force; Get-BriefBridgeVersion'"
        )
        
        output = version_test.output.decode('utf-8')
        assert "Name" in output
        assert "Version" in output
        assert "PowerShellVersion" in output
    
    def _run_regression_tests(self, container) -> None:
        """Run direct cmdlet tests without Pester framework"""
        
        # Test cmdlet can be called multiple times
        repeat_test = container.exec(
            "pwsh -c 'Import-Module /host/BriefBridgeEditor.psd1 -Force; Get-BriefBridgeVersion; Get-BriefBridgeVersion'"
        )
        assert repeat_test.exit_code == 0
        repeat_output = repeat_test.output.decode('utf-8')
        assert repeat_output.count("Brief Bridge Editor") >= 2
        
        # Test cmdlet works with PowerShell pipeline
        pipeline_test = container.exec(
            "pwsh -c 'Import-Module /host/BriefBridgeEditor.psd1 -Force; Get-BriefBridgeVersion | Select-Object Name, Version'"
        )
        assert pipeline_test.exit_code == 0
        
        # Test module supports re-import
        reimport_test = container.exec(
            "pwsh -c 'Import-Module /host/BriefBridgeEditor.psd1 -Force; Import-Module /host/BriefBridgeEditor.psd1 -Force; Get-BriefBridgeVersion'"
        )
        assert reimport_test.exit_code == 0
        
        # Test cmdlet is discoverable
        command_test = container.exec(
            "pwsh -c 'Import-Module /host/BriefBridgeEditor.psd1 -Force; Get-Command Get-BriefBridgeVersion'"
        )
        assert command_test.exit_code == 0
        command_output = command_test.output.decode('utf-8')
        assert "Get-BriefBridgeVersion" in command_output
    
    def _run_pester_tests(self, container) -> None:
        """Run Pester framework tests"""
        pester_check = container.exec("pwsh -c 'Get-Module -ListAvailable -Name Pester'")
        
        if pester_check.exit_code == 0:
            pester_test = container.exec(
                "pwsh -c 'cd /host; Import-Module Pester; Invoke-Pester -Path ./BriefBridgeEditor.Tests.ps1'"
            )
            pester_output = pester_test.output.decode()
            
            if pester_test.exit_code == 0:
                assert "Tests Passed:" in pester_output
            else:
                pytest.fail(f"Pester tests failed: {pester_output}")
        else:
            pytest.skip("Pester not available in container")