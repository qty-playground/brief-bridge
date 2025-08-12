class TestPowerShellContainer:
    
    def test_can_execute_basic_powershell_commands(self, powershell_container):
        execution_result = powershell_container.exec("pwsh -c 'Write-Output \"Hello from PowerShell\"'")
        
        assert execution_result.exit_code == 0
        assert "Hello from PowerShell" in execution_result.output.decode('utf-8')
        
    def test_powershell_version_is_available(self, powershell_container):
        version_result = powershell_container.exec("pwsh --version")
        
        assert version_result.exit_code == 0
        assert "7." in version_result.output.decode('utf-8')
        
    def test_container_includes_required_utilities(self, powershell_container):
        curl_result = powershell_container.exec("curl --version")
        assert curl_result.exit_code == 0
        assert "curl" in curl_result.output.decode('utf-8')
        
        jq_result = powershell_container.exec("jq --version")
        assert jq_result.exit_code == 0
        
    def test_can_process_json_with_jq(self, powershell_container):
        json_processing_result = powershell_container.exec(
            "echo '{\"name\": \"test\", \"version\": \"1.0\"}' | jq .name"
        )
        
        assert json_processing_result.exit_code == 0
        assert '"test"' in json_processing_result.output.decode('utf-8')