# Calendar Cleaner for Windows - Vedic Calendar Event Remover
# PowerShell Script
# This script removes VAR and DUS events from ICS files

param(
    [string]$InputDir = "input_ics_files",
    [string]$OutputDir = "output_ics_files",
    [string]$StartDate = "2025-07-01",
    [string]$EndDate = "2025-12-31"
)

function Write-Header {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "   Vedic Calendar Event Cleaner" -ForegroundColor Cyan
    Write-Host "   Windows PowerShell Script" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Test-Prerequisites {
    # Check if Python is installed
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found"
        }
        Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please install Python from https://python.org" -ForegroundColor Yellow
        Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Check if the calendar_invite_remover.py script exists
    if (-not (Test-Path "calendar_invite_remover.py")) {
        Write-Host "❌ ERROR: calendar_invite_remover.py not found in current directory" -ForegroundColor Red
        Write-Host "Please ensure the script is in the same folder as this PowerShell file" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✓ calendar_invite_remover.py found" -ForegroundColor Green
}

function Initialize-Directories {
    # Create directories if they don't exist
    if (-not (Test-Path $InputDir)) {
        Write-Host "Creating input directory: $InputDir" -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $InputDir | Out-Null
    }

    if (-not (Test-Path $OutputDir)) {
        Write-Host "Creating output directory: $OutputDir" -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $OutputDir | Out-Null
    }

    Write-Host ""
    Write-Host "Current settings:" -ForegroundColor Cyan
    Write-Host "  Input directory: $InputDir" -ForegroundColor White
    Write-Host "  Output directory: $OutputDir" -ForegroundColor White
    Write-Host "  Date range: $StartDate to $EndDate" -ForegroundColor White
    Write-Host ""
}

function Get-ICSFiles {
    $icsFiles = Get-ChildItem -Path $InputDir -Filter "*.ics" -ErrorAction SilentlyContinue
    
    if ($icsFiles.Count -eq 0) {
        Write-Host "No ICS files found in $InputDir" -ForegroundColor Red
        Write-Host "Please place your ICS files in the $InputDir folder" -ForegroundColor Yellow
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }

    Write-Host "Found $($icsFiles.Count) ICS file(s) in $InputDir" -ForegroundColor Green
    Write-Host ""
    Write-Host "Available ICS files:" -ForegroundColor Cyan
    $icsFiles | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }
    Write-Host ""

    return $icsFiles
}

function Show-Menu {
    Write-Host "Choose an option:" -ForegroundColor Cyan
    Write-Host "1. Process all ICS files in $InputDir" -ForegroundColor White
    Write-Host "2. Process a specific file" -ForegroundColor White
    Write-Host "3. Exit" -ForegroundColor White
    Write-Host ""
    $choice = Read-Host "Enter your choice (1-3)"
    return $choice
}

function Process-SingleFile {
    param([string]$FilePath)
    
    $fileName = [System.IO.Path]::GetFileNameWithoutExtension($FilePath)
    $outputFile = Join-Path $OutputDir "$fileName`_cleaned.ics"
    
    Write-Host "Processing: $([System.IO.Path]::GetFileName($FilePath))" -ForegroundColor Cyan
    Write-Host "  Input: $FilePath" -ForegroundColor Gray
    Write-Host "  Output: $outputFile" -ForegroundColor Gray
    
    # Step 1: Remove VAR events
    Write-Host "  Step 1: Removing VAR events..." -ForegroundColor Yellow
    $varResult = & python calendar_invite_remover.py $FilePath --pattern "VAR" --start-date $StartDate --end-date $EndDate
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ❌ ERROR: Failed to remove VAR events" -ForegroundColor Red
        return $false
    }
    
    # Step 2: Remove DUS events from the cleaned file
    Write-Host "  Step 2: Removing DUS events..." -ForegroundColor Yellow
    $dusResult = & python calendar_invite_remover.py $outputFile --pattern "DUS" --start-date $StartDate --end-date $EndDate
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ❌ ERROR: Failed to remove DUS events" -ForegroundColor Red
        return $false
    }
    
    Write-Host "  ✓ SUCCESS: File processed successfully" -ForegroundColor Green
    return $true
}

function Process-AllFiles {
    $icsFiles = Get-ICSFiles
    $successCount = 0
    $totalCount = $icsFiles.Count
    
    Write-Host "Processing all ICS files..." -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($file in $icsFiles) {
        if (Process-SingleFile $file.FullName) {
            $successCount++
        }
        Write-Host ""
    }
    
    Write-Host "Processing complete: $successCount/$totalCount files successful" -ForegroundColor Cyan
}

function Process-SpecificFile {
    $icsFiles = Get-ICSFiles
    
    Write-Host "Available files:" -ForegroundColor Cyan
    for ($i = 0; $i -lt $icsFiles.Count; $i++) {
        Write-Host "$($i + 1). $($icsFiles[$i].Name)" -ForegroundColor White
    }
    Write-Host ""
    
    do {
        $fileChoice = Read-Host "Enter file number (1-$($icsFiles.Count))"
        $fileIndex = [int]$fileChoice - 1
    } while ($fileIndex -lt 0 -or $fileIndex -ge $icsFiles.Count)
    
    $selectedFile = $icsFiles[$fileIndex]
    Write-Host ""
    Process-SingleFile $selectedFile.FullName
}

function Show-Summary {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "    Processing Complete" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Show output files
    $outputFiles = Get-ChildItem -Path $OutputDir -Filter "*_cleaned_cleaned.ics" -ErrorAction SilentlyContinue
    if ($outputFiles.Count -gt 0) {
        Write-Host "Output files created in $OutputDir:" -ForegroundColor Green
        $outputFiles | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }
    }
    
    # Show cancellation files
    $cancellationFiles = Get-ChildItem -Path $OutputDir -Filter "*_cleaned_cleaned_cancellations.ics" -ErrorAction SilentlyContinue
    if ($cancellationFiles.Count -gt 0) {
        Write-Host ""
        Write-Host "Cancellation files for import:" -ForegroundColor Green
        $cancellationFiles | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "    Import Instructions" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "For Windows Outlook:" -ForegroundColor Yellow
    Write-Host "1. Open Outlook" -ForegroundColor White
    Write-Host "2. Go to File > Open & Export > Import/Export" -ForegroundColor White
    Write-Host "3. Choose 'Import an iCalendar (.ics) file'" -ForegroundColor White
    Write-Host "4. Select the cancellation file: *_cleaned_cleaned_cancellations.ics" -ForegroundColor White
    Write-Host "5. Choose your calendar and import" -ForegroundColor White
    Write-Host ""
    
    Write-Host "For macOS Calendar:" -ForegroundColor Yellow
    Write-Host "1. Double-click the cancellation file" -ForegroundColor White
    Write-Host "2. If import fails, use the cleaned file instead" -ForegroundColor White
    Write-Host "3. Or create a new calendar and import the cleaned file" -ForegroundColor White
    Write-Host ""
    
    Write-Host "For Google Calendar:" -ForegroundColor Yellow
    Write-Host "1. Go to Settings > Import & Export" -ForegroundColor White
    Write-Host "2. Upload the cancellation file" -ForegroundColor White
    Write-Host "3. Choose your calendar and import" -ForegroundColor White
    Write-Host ""
}

# Main script execution
try {
    Write-Header
    Test-Prerequisites
    Initialize-Directories
    
    do {
        $choice = Show-Menu
        
        switch ($choice) {
            "1" { Process-AllFiles; Show-Summary }
            "2" { Process-SpecificFile; Show-Summary }
            "3" { 
                Write-Host ""
                Write-Host "Thank you for using Vedic Calendar Event Cleaner!" -ForegroundColor Green
                Write-Host ""
                break
            }
            default { 
                Write-Host "Invalid choice. Please try again." -ForegroundColor Red
                Write-Host ""
            }
        }
        
        if ($choice -ne "3") {
            Write-Host ""
            $continue = Read-Host "Press Enter to continue or 'q' to quit"
            if ($continue -eq "q") { break }
        }
    } while ($choice -ne "3")
}
catch {
    Write-Host "An error occurred: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
} 