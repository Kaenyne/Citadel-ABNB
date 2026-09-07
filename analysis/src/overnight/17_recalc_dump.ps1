<#
  17_recalc_dump.ps1 - native Excel recalculation driver for the ABNB driver model.

  Opens the workbook in real Excel (COM), optionally writes a scenario selector value, runs
  Application.CalculateFullRebuild(), and dumps every non-empty cell (sheet, address, row, col,
  is_formula, formula, value, is_number, error) to CSV. This is the only step of the build that
  needs Windows plus a licensed desktop Excel; everything downstream reads the CSV it writes.

  Moved into the repository from a session scratchpad on 6 Sep 2026 (workstream 24, audit findings
  A07/A13): the reconciliation evidence has to be regenerable from a clean checkout. Self-contained:
  every default path is derived from $PSScriptRoot, no user profile or sibling worktree is referenced.

  USAGE
    powershell -NoProfile -ExecutionPolicy Bypass -File analysis/src/overnight/17_recalc_dump.ps1
      # base dump -> data/processed/overnight/17_excel_recalc_dump.csv

    ... -ScenarioValue 1 -OutCsv <dir>\17_dump_after_scen1.csv -MetaTxt <dir>\17_meta_scen1.txt
    ... -ScenarioValue 3 -OutCsv <dir>\17_dump_after_scen3.csv
      # the two off-base dumps that 17_scenario_switch.py compares against the base dump

    ... -InPath <scratch copy with a deliberately altered cell> -OutCsv <scratch>\dump.csv
      # the negative control used by the 17_excel_audit.py exit-code tests

  PARAMETERS
    -InPath         workbook to open           (default: model/ABNB_driver_model.xlsx)
    -OutCsv         cell dump destination      (default: data/processed/overnight/17_excel_recalc_dump.csv)
    -SaveAs         optional .xlsx path to save the recalculated copy to (xlsx format 51)
    -NamesCsv       optional named-range dump (name, refers_to, value)
    -MetaTxt        optional metadata file (Excel version, calc state, iteration, circular refs, cell count)
    -ScenarioValue  0 = leave the workbook as shipped; 1/2/3 = Bear/Base/Bull
    -ScenarioCell   sheet!address the scenario value is written to (default Inputs!B4, the named
                    range `Scenario`; the pre-WS17 workbook used Inputs!B3)

  EXIT STATUS  0 on a completed dump; 2 if the workbook is missing; 1 if Excel cannot open or
  recalculate it. Excel is quit and released in a finally block, so a failure leaves no orphan
  EXCEL.EXE holding the file.
#>
param(
  [string]$InPath,
  [string]$OutCsv,
  [string]$SaveAs,
  [string]$NamesCsv,
  [string]$MetaTxt,
  [int]$ScenarioValue = 0,
  [string]$ScenarioCell = "Inputs!B4"
)

$ErrorActionPreference = "Stop"

# ------------------------------------------------------------------ repo-relative path defaults
# $PSScriptRoot is <repo>/analysis/src/overnight, so the project root is three levels up.
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
if (-not $InPath)  { $InPath  = Join-Path $Root "model\ABNB_driver_model.xlsx" }
if (-not $OutCsv)  { $OutCsv  = Join-Path $Root "data\processed\overnight\17_excel_recalc_dump.csv" }
if (-not (Test-Path $InPath)) { Write-Error "workbook not found: $InPath"; exit 2 }
$InPath = (Resolve-Path $InPath).Path
$outDir = Split-Path -Parent $OutCsv
if ($outDir -and -not (Test-Path $outDir)) { New-Item -ItemType Directory -Force $outDir | Out-Null }

$errmap = @{
  -2146826288 = "#NULL!"
  -2146826281 = "#DIV/0!"
  -2146826273 = "#VALUE!"
  -2146826265 = "#REF!"
  -2146826259 = "#NAME?"
  -2146826252 = "#NUM!"
  -2146826246 = "#N/A"
  -2146826245 = "#GETTING_DATA"
}

$xl = $null
$wb = $null
try {
  $xl = New-Object -ComObject Excel.Application
  $xl.Visible = $false
  $xl.DisplayAlerts = $false
  $xl.ScreenUpdating = $false
  $xl.AskToUpdateLinks = $false

  $meta = New-Object System.Collections.Generic.List[string]
  $meta.Add("script=17_recalc_dump.ps1")
  $meta.Add("in_path=" + $InPath)
  $meta.Add("excel_version=" + $xl.Version)
  $meta.Add("iteration_before=" + $xl.Iteration)
  $meta.Add("calculation_before=" + $xl.Calculation)

  $wb = $xl.Workbooks.Open($InPath, 0, $false)

  if ($ScenarioValue -gt 0) {
    $parts = $ScenarioCell.Split("!")
    $wb.Worksheets.Item($parts[0]).Range($parts[1]).Value2 = $ScenarioValue
    $meta.Add("scenario_set=" + $ScenarioCell + "=" + $ScenarioValue)
  }

  $xl.CalculateFullRebuild()
  $meta.Add("calc_state_after=" + $xl.CalculationState)
  $meta.Add("iteration_after=" + $xl.Iteration)
  $meta.Add("max_iterations=" + $xl.MaxIterations)
  $meta.Add("max_change=" + $xl.MaxChange)
  $meta.Add("statusbar=" + [string]$xl.StatusBar)

  # circular reference probe: Excel puts the circular cell address on the status bar and
  # ActiveSheet.CircularReference returns a Range when one exists.
  foreach ($ws in $wb.Worksheets) {
    try {
      $cr = $ws.CircularReference
      if ($cr -ne $null) { $meta.Add("circular=" + $ws.Name + "!" + $cr.Address()) }
    } catch { }
  }

  $rows = New-Object System.Collections.Generic.List[object]
  foreach ($ws in $wb.Worksheets) {
    $used = $ws.UsedRange
    $nr = $used.Rows.Count
    $nc = $used.Columns.Count
    $r0 = $used.Row
    $c0 = $used.Column
    if ($nr -eq 1 -and $nc -eq 1) {
      $vals = New-Object 'object[,]' 1,1
      $fmls = New-Object 'object[,]' 1,1
      $vals[0,0] = $used.Value2
      $fmls[0,0] = $used.Formula
    } else {
      $vals = $used.Value2
      $fmls = $used.Formula
    }
    for ($i = 1; $i -le $nr; $i++) {
      for ($j = 1; $j -le $nc; $j++) {
        if ($nr -eq 1 -and $nc -eq 1) { $v = $vals[0,0]; $f = $fmls[0,0] }
        else { $v = $vals[$i,$j]; $f = $fmls[$i,$j] }
        if (($v -eq $null -or "$v" -eq "") -and ($f -eq $null -or "$f" -eq "")) { continue }
        $addr = $ws.Cells.Item($r0 + $i - 1, $c0 + $j - 1).Address($false, $false)
        $err = ""
        $vout = $v
        if ($v -is [int] -and $errmap.ContainsKey([int]$v)) { $err = $errmap[[int]$v]; $vout = $err }
        elseif ($v -is [double] -and $errmap.ContainsKey([int]$v)) { $err = $errmap[[int]$v]; $vout = $err }
        $isf = ($f -ne $null -and "$f".StartsWith("="))
        $rows.Add([pscustomobject]@{
          sheet   = $ws.Name
          address = $addr
          row     = $r0 + $i - 1
          col     = $c0 + $j - 1
          is_formula = $isf
          formula = if ($isf) { "$f" } else { "" }
          value   = "$vout"
          is_number = ($v -is [double] -and $err -eq "")
          error   = $err
        })
      }
    }
  }
  $meta.Add("cells_dumped=" + $rows.Count)
  $rows | Export-Csv -Path $OutCsv -NoTypeInformation -Encoding UTF8

  if ($NamesCsv) {
    $nrows = New-Object System.Collections.Generic.List[object]
    foreach ($n in $wb.Names) {
      $rt = ""
      try { $rt = $n.RefersTo } catch { $rt = "<err>" }
      $vv = ""
      try { $vv = "$($n.RefersToRange.Value2)" } catch { $vv = "<not a range>" }
      $nrows.Add([pscustomobject]@{ name = $n.Name; refers_to = $rt; value = $vv })
    }
    $meta.Add("named_ranges=" + $nrows.Count)
    if ($nrows.Count -gt 0) { $nrows | Export-Csv -Path $NamesCsv -NoTypeInformation -Encoding UTF8 }
    else { "name,refers_to,value" | Out-File -FilePath $NamesCsv -Encoding UTF8 }
  }

  if ($SaveAs) { $wb.SaveAs($SaveAs, 51) }
  if ($MetaTxt) { $meta | Out-File -FilePath $MetaTxt -Encoding UTF8 }
  $meta | ForEach-Object { Write-Output $_ }
}
catch {
  Write-Error ("17_recalc_dump.ps1 failed: " + $_.Exception.Message)
  exit 1
}
finally {
  if ($wb -ne $null) { try { $wb.Close($false) } catch { } }
  if ($xl -ne $null) {
    try { $xl.Quit() } catch { }
    try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null } catch { }
  }
}
