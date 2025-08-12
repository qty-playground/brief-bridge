# Pester tests for Brief Bridge Editor PowerShell Module

BeforeAll {
    # Import the module for testing
    Import-Module "$PSScriptRoot/BriefBridgeEditor.psd1" -Force
}

Describe "BriefBridgeEditor Module Tests" {
    
    Context "Module Import" {
        It "Should import the module successfully" {
            Get-Module BriefBridgeEditor | Should -Not -BeNullOrEmpty
        }
        
        It "Should have the correct module version" {
            $module = Get-Module BriefBridgeEditor
            $module.Version.ToString() | Should -Be "1.0.0"
        }
    }
    
    Context "Get-BriefBridgeVersion Cmdlet" {
        It "Should be available as an exported function" {
            Get-Command Get-BriefBridgeVersion -Module BriefBridgeEditor | Should -Not -BeNullOrEmpty
        }
        
        It "Should return version information object" {
            $result = Get-BriefBridgeVersion
            $result | Should -Not -BeNullOrEmpty
            $result | Should -BeOfType [PSCustomObject]
        }
        
        It "Should return correct editor name" {
            $result = Get-BriefBridgeVersion
            $result.Name | Should -Be "Brief Bridge Editor"
        }
        
        It "Should return correct version number" {
            $result = Get-BriefBridgeVersion
            $result.Version | Should -Be "1.0.0"
        }
        
        It "Should include PowerShell version information" {
            $result = Get-BriefBridgeVersion
            $result.PowerShellVersion | Should -Not -BeNullOrEmpty
            $result.PowerShellVersion | Should -Match "^\d+\.\d+\.\d+"
        }
        
        It "Should include platform information" {
            $result = Get-BriefBridgeVersion
            $result.Platform | Should -Not -BeNullOrEmpty
        }
        
        It "Should include build date" {
            $result = Get-BriefBridgeVersion
            $result.BuildDate | Should -Not -BeNullOrEmpty
            # Verify it's a valid date format
            { [DateTime]::Parse($result.BuildDate) } | Should -Not -Throw
        }
        
        It "Should include description" {
            $result = Get-BriefBridgeVersion
            $result.Description | Should -Be "A powerful text editor with advanced capabilities"
        }
    }
}

AfterAll {
    # Clean up - remove the module
    Remove-Module BriefBridgeEditor -Force -ErrorAction SilentlyContinue
}