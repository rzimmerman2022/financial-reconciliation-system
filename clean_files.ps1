<#
.SYNOPSIS
    Cleans null bytes from files and converts them to Unix line endings.
.DESCRIPTION
    This script recursively finds all Python files (*.py) in the current directory
    and its subdirectories. For each file, it removes null bytes and converts
    Windows-style (CRLF) line endings to Unix-style (LF). The files are saved
    with UTF-8 encoding without a Byte Order Mark (BOM).
#>

function Clean-File {
    param(
        [Parameter(Mandatory=$true)]
        [string]$FilePath
    )

    try {
        # Read the entire file as a single string
        $content = Get-Content -Path $FilePath -Raw

        # Remove null bytes and then convert Windows line endings to Unix
        $cleanedContent = $content.Replace([char]0x00, "").Replace("`r`n", "`n")

        # Create a UTF8Encoding object that does not write a Byte Order Mark (BOM)
        $utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)

        # Write the cleaned content back to the file using the specified encoding
        [System.IO.File]::WriteAllText($FilePath, $cleanedContent, $utf8WithoutBom)

        Write-Host "? Cleaned: $FilePath" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "? Error cleaning $($FilePath): $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function main {
    Write-Host "Searching for Python files..."
    # Recursively get all files with a .py extension from the current directory
    $pythonFiles = Get-ChildItem -Path . -Recurse -Filter '*.py'

    if ($null -eq $pythonFiles) {
        Write-Host "No Python files were found."
        return
    }

    $fileCount = ($pythonFiles | Measure-Object).Count
    Write-Host "Found $fileCount Python file(s) to clean."

    $cleanedCount = 0
    foreach ($file in $pythonFiles) {
        if (Clean-File -FilePath $file.FullName) {
            $cleanedCount++
        }
    }

    Write-Host "`nCleaned $cleanedCount/$fileCount files successfully."
}

# Execute the main function of the script
main
