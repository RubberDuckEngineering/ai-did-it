<#
.SYNOPSIS
    Start the next link of an AI Did It lane as a detached Claude Code session.

.DESCRIPTION
    Run from the project root:
      spawn-lane.ps1 -Lane <id> -Link <stage> -PromptFile <path> [-Mode claude|claude-remote] [-DryRun]

    -Lane        lane id, ^[a-z0-9][a-z0-9-]{0,62}$ (case-sensitive)
    -Link        ideate | draft | iterate | deliver | investigate | tidy
    -PromptFile  existing, non-empty file holding the link's prompt (max 32000 chars)
    -Mode        claude (default): claude -p "<prompt>"
                 claude-remote:    claude --remote-control "<lane>-<link>" "<prompt>"
    -DryRun      print one line "DRY-RUN: <bin> <args...>" and exit 0; creates nothing.
                 Newlines in the prompt are shown as \n and \r so the line stays single.

    The claude binary is $env:AIDIDIT_CLAUDE_BIN if set, else `claude` on PATH. Batch shims
    (.cmd/.bat) are refused: cmd.exe re-parses their arguments, which would let prompt text
    act as shell syntax.
    Output on success: SPAWNED lane=<lane> link=<link> pid=<pid> log=<path>
    stdout goes to <link>.log; stderr goes to <link>.err.log beside it, because Start-Process
    cannot send both streams to one file.
    Exit codes: 0 ok, 2 usage/validation error, 3 claude binary not found.
    The prompt is encoded as a single argv element; it is never evaluated by a shell.
#>
[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$Lane,
    [string]$Link,
    [string]$PromptFile,
    [string]$Mode = 'claude',
    [switch]$DryRun,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$UnexpectedArguments
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$LanePattern = '^[a-z0-9][a-z0-9-]{0,62}\z'
$ValidLinks = @('ideate', 'draft', 'iterate', 'deliver', 'investigate', 'tidy')
$ValidModes = @('claude', 'claude-remote')
$BatchShimExtensions = @('.cmd', '.bat')
$MaxPromptChars = 32000
$LedgerRoot = '.specify/aididit/lanes'
$ExitUsage = 2
$ExitNoClaude = 3

function Stop-WithUsage([string]$Message) {
    [Console]::Error.WriteLine("spawn-lane: $Message")
    [Console]::Error.WriteLine('Usage: spawn-lane.ps1 -Lane <id> -Link <stage> -PromptFile <path> [-Mode claude|claude-remote] [-DryRun]')
    exit $ExitUsage
}

# Encodes one argument so the child's argv parser (Windows CommandLineToArgvW rules, which
# .NET also applies on Unix) yields exactly the original string.
function ConvertTo-ArgvToken([string]$Value) {
    if ($Value.Length -gt 0 -and $Value -notmatch '[\s"]') { return $Value }
    $builder = [System.Text.StringBuilder]::new('"')
    $pendingBackslashes = 0
    foreach ($character in $Value.ToCharArray()) {
        if ($character -eq [char]'\') { $pendingBackslashes++; continue }
        $repeat = if ($character -eq [char]'"') { 2 * $pendingBackslashes + 1 } else { $pendingBackslashes }
        [void]$builder.Append([char]'\', $repeat).Append($character)
        $pendingBackslashes = 0
    }
    [void]$builder.Append([char]'\', 2 * $pendingBackslashes).Append([char]'"')
    return $builder.ToString()
}

if ($UnexpectedArguments) { Stop-WithUsage "unknown argument: $($UnexpectedArguments -join ' ')" }
if ([string]::IsNullOrEmpty($Lane)) { Stop-WithUsage '-Lane is required' }
if ([string]::IsNullOrEmpty($Link)) { Stop-WithUsage '-Link is required' }
if ([string]::IsNullOrEmpty($PromptFile)) { Stop-WithUsage '-PromptFile is required' }
if ($Lane -cnotmatch $LanePattern) { Stop-WithUsage "invalid lane id '$Lane' (must match ^[a-z0-9][a-z0-9-]{0,62}$)" }
if ($ValidLinks -cnotcontains $Link) { Stop-WithUsage "invalid link '$Link' (one of: $($ValidLinks -join ' '))" }
if ($ValidModes -cnotcontains $Mode) { Stop-WithUsage "invalid mode '$Mode' (claude or claude-remote)" }
if (-not (Test-Path -LiteralPath $PromptFile -PathType Leaf)) { Stop-WithUsage "prompt file not found: $PromptFile" }

$promptPath = (Resolve-Path -LiteralPath $PromptFile).ProviderPath
$prompt = [System.IO.File]::ReadAllText($promptPath).TrimEnd("`r", "`n")
if ($prompt.Length -eq 0) { Stop-WithUsage "prompt file is empty: $PromptFile" }
if ($prompt.Length -gt $MaxPromptChars) { Stop-WithUsage "prompt exceeds $MaxPromptChars characters" }

$claudeBin = if ($env:AIDIDIT_CLAUDE_BIN) { $env:AIDIDIT_CLAUDE_BIN } else { 'claude' }
$claudeArgs = if ($Mode -eq 'claude-remote') {
    @('--remote-control', "${Lane}-${Link}", $prompt)
} else {
    @('-p', $prompt)
}

if ($DryRun) {
    $line = "DRY-RUN: $claudeBin " + ($claudeArgs -join ' ')
    Write-Output $line.Replace("`r", '\r').Replace("`n", '\n')
    exit 0
}

$resolved = Get-Command -Name $claudeBin -CommandType Application -ErrorAction SilentlyContinue |
    Where-Object { $BatchShimExtensions -notcontains $_.Extension } |
    Select-Object -First 1
if ($null -eq $resolved) {
    [Console]::Error.WriteLine("spawn-lane: claude binary not found: $claudeBin (set AIDIDIT_CLAUDE_BIN or put claude on PATH; .cmd/.bat shims are refused)")
    exit $ExitNoClaude
}

$laneDir = "$LedgerRoot/$Lane"
$logPath = "$laneDir/$Link.log"
$projectRoot = (Get-Location).ProviderPath
$null = New-Item -ItemType Directory -Path (Join-Path $projectRoot $laneDir) -Force

$startArgs = @{
    FilePath               = $resolved.Source
    ArgumentList           = ($claudeArgs | ForEach-Object { ConvertTo-ArgvToken $_ }) -join ' '
    RedirectStandardOutput = Join-Path $projectRoot $logPath
    RedirectStandardError  = Join-Path $projectRoot "$laneDir/$Link.err.log"
    PassThru               = $true
}
if ([System.Environment]::OSVersion.Platform -ne [System.PlatformID]::Win32NT) {
    $startArgs.RedirectStandardInput = '/dev/null'
}
$process = Start-Process @startArgs

Write-Output "SPAWNED lane=$Lane link=$Link pid=$($process.Id) log=$logPath"
exit 0
