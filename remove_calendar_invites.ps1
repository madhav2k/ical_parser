# Calendar Invite Remover - PowerShell Script
# This PowerShell script makes it easy to run the calendar invite remover on Windows

param(
    [Parameter(Mandatory=$false)]
    [string]$InputFile,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputFile,
    
    [Parameter(Mandatory=$false)]
    [switch]$RemoveInvites,
    
    [Parameter(Mandatory=$false)]
    [string]$Pattern,
    
    [Parameter(Mandatory=$false)]
    [string]$StartDate,
    
    [Parameter(Mandatory=$false)]
    [string]$EndDate,
    
    [Parameter(Mandatory=$false)]
    [switch]$RemoveDuplicates,
    
    [Parameter(Mandatory=$false)]
    [string[]]$KeepCategories,
    
    [Parameter(Mandatory=$false)]
    [string[]]$RemoveCategories,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose,
    
    [Parameter(Mandatory=$false)]
    [switch]$Help
)

function Show-Help {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Calendar Invite Remover for Windows" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\remove_calendar_invites.ps1 -InputFile calendar.ics [options]"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\remove_calendar_invites.ps1 -InputFile calendar.ics"
    Write-Host "  .\remove_calendar_invites.ps1 -InputFile calendar.ics -RemoveInvites"
    Write-Host "  .\remove_calendar_invites.ps1 -InputFile calendar.ics -Pattern 'zoom|teams'"
    Write-Host "  .\remove_calendar_invites.ps1 -InputFile calendar.ics -StartDate '2024-01-01' -EndDate '2024-01-31'"
    Write-Host "  .\remove_calendar_invites.ps1 -InputFile calendar.ics -RemoveDuplicates"
    Write-Host "  .\remove_calendar_invites.ps1 -InputFile calendar.ics -DryRun"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -InputFile         Path to input ICS file (required)"
    Write-Host "  -OutputFile        Path to output ICS file (optional)"
    Write-Host "  -RemoveInvites     Remove meeting/invite events"
    Write-Host "  -Pattern           Regex pattern to match events for removal"
    Write-Host "  -StartDate         Start date for filtering (YYYY-MM-DD)"
    Write-Host "  -EndDate           End date for filtering (YYYY-MM-DD)"
    Write-Host "  -RemoveDuplicates  Remove duplicate events"
    Write-Host "  -KeepCategories    Keep only events with these categories"
    Write-Host "  -RemoveCategories  Remove events with these categories"
    Write-Host "  -DryRun            Show what would be removed without making changes"
    Write-Host "  -Verbose           Enable verbose logging"
    Write-Host "  -Help              Show this help message"
    Write-Host ""
}

# Show help if requested or no input file provided
if ($Help -or -not $InputFile) {
    Show-Help
    exit
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org" -ForegroundColor Red
    exit 1
}

# Check if required packages are installed
Write-Host "Checking required packages..." -ForegroundColor Yellow
try {
    python -c "import icalendar" 2>$null
    Write-Host "Required packages found" -ForegroundColor Green
} catch {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    try {
        pip install icalendar
        Write-Host "Required packages installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to install required packages" -ForegroundColor Red
        exit 1
    }
}

# Build command arguments
$args = @($InputFile)

if ($OutputFile) {
    $args += "-o", $OutputFile
}

if ($RemoveInvites) {
    $args += "--remove-invites"
}

if ($Pattern) {
    $args += "--pattern", $Pattern
}

if ($StartDate) {
    $args += "--start-date", $StartDate
}

if ($EndDate) {
    $args += "--end-date", $EndDate
}

if ($RemoveDuplicates) {
    $args += "--remove-duplicates"
}

if ($KeepCategories) {
    $args += "--keep-categories"
    $args += $KeepCategories
}

if ($RemoveCategories) {
    $args += "--remove-categories"
    $args += $RemoveCategories
}

if ($DryRun) {
    $args += "--dry-run"
}

if ($Verbose) {
    $args += "--verbose"
}

# Run the Python script
Write-Host "Running calendar invite remover..." -ForegroundColor Yellow
Write-Host "Command: python calendar_invite_remover.py $($args -join ' ')" -ForegroundColor Gray

try {
    python calendar_invite_remover.py @args
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Script completed successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "ERROR: Script failed to run successfully" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to run script: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} 