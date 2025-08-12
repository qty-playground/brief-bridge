@{
    # Module manifest for Brief Bridge Editor
    RootModule = 'BriefBridgeEditor.psm1'
    ModuleVersion = '1.0.0'
    GUID = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    Author = 'Brief Bridge Team'
    CompanyName = 'Brief Bridge'
    Copyright = '(c) Brief Bridge Team. All rights reserved.'
    Description = 'PowerShell module for Brief Bridge Editor - A powerful text editor with advanced capabilities'
    
    # PowerShell version requirements
    PowerShellVersion = '7.0'
    
    # Functions to export from this module
    FunctionsToExport = @(
        'Get-BriefBridgeVersion'
    )
    
    # Cmdlets to export from this module
    CmdletsToExport = @()
    
    # Variables to export from this module
    VariablesToExport = @()
    
    # Aliases to export from this module
    AliasesToExport = @()
    
    # Private data to pass to the module specified in RootModule/ModuleToProcess
    PrivateData = @{
        PSData = @{
            Tags = @('Editor', 'Text', 'Development')
            ProjectUri = 'https://github.com/brief-bridge/brief-bridge'
            ReleaseNotes = 'Initial release of Brief Bridge Editor PowerShell module'
        }
    }
}