$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../../..')).Path
$outputPath = Join-Path $taskRoot 'outputs/gbv-event-20260915'
$bookPath = Join-Path $outputPath 'ABNB_GBV_guidance.xlsx'
$rawHash = (Get-FileHash -LiteralPath $bookPath -Algorithm SHA256).Hash
$excelApp = $null
$excelBook = $null
try {
    $excelApp = New-Object -ComObject Excel.Application
    $excelApp.Visible = $false
    $excelApp.DisplayAlerts = $false
    $excelApp.EnableEvents = $false
    $excelApp.AutomationSecurity = 3
    $excelBook = $excelApp.Workbooks.Open($bookPath, 0, $false)
    $excelApp.CalculateFullRebuild()
    $conversion = $excelBook.Worksheets.Item('Conversion')
    $inputs = $excelBook.Worksheets.Item('Inputs')
    $decision = $excelBook.Worksheets.Item('Decision')
    $baseGuide = [double]$conversion.Range('D13').Value2
    if ([Math]::Abs($baseGuide - 3123.419115173388) -gt 0.0000001) { throw 'Native guide tie-out failed' }
    if ([Math]::Abs([double]$conversion.Range('D19').Value2 - 17.999878083750446) -gt 0.0000001) { throw 'Native gap tie-out failed' }
    if ([double]$decision.Range('D10').Value2 -ne 4730) { throw 'Observed Q3 guide failed' }
    $oldGBV = $inputs.Range('C8').Value2
    try {
        $inputs.Range('C8').Value2 = [double]$oldGBV * 1.01
        $excelApp.CalculateFullRebuild()
        if ([double]$conversion.Range('D13').Value2 -le $baseGuide) { throw 'Native GBV propagation failed' }
    } finally { $inputs.Range('C8').Value2 = $oldGBV }
    $oldCushion = $inputs.Range('D15').Value2
    $benchmark = [double]$conversion.Range('D18').Value2
    try {
        $inputs.Range('D15').Value2 = [double]0
        $excelApp.CalculateFullRebuild()
        if ([Math]::Abs([double]$conversion.Range('D13').Value2 - [double]$conversion.Range('D11').Value2) -gt 0.0000001) { throw 'Native zero cushion failed' }
        if ([double]$conversion.Range('D18').Value2 -ne $benchmark) { throw 'Benchmark moved with our cushion' }
        $inputs.Range('D15').ClearContents()
        $excelApp.CalculateFullRebuild()
        if ($conversion.Range('D13').Value2 -ne 'n.a.') { throw 'Native missing cushion failed' }
    } finally { $inputs.Range('D15').Value2 = $oldCushion }
    $excelApp.CalculateFullRebuild()
    if ([Math]::Abs([double]$conversion.Range('D13').Value2 - $baseGuide) -gt 0.0000001) { throw 'Native restoration failed' }
    $chartCounts = @()
    for ($sheetIndex = 1; $sheetIndex -le $excelBook.Worksheets.Count; $sheetIndex++) {
        $sheet = $excelBook.Worksheets.Item($sheetIndex)
        $chartCounts += @{sheet=$sheet.Name; charts=$sheet.ChartObjects().Count}
        for ($chartIndex = 1; $chartIndex -le $sheet.ChartObjects().Count; $chartIndex++) {
            $chart = $sheet.ChartObjects($chartIndex).Chart
            $chart.Refresh()
        }
    }
    $decision.Activate()
    $decision.Range('B2').Select()
    $excelApp.ActiveWindow.Zoom = 85
    $excelBook.Save()
    $receipt = @{status='pass'; engine='Microsoft Excel COM'; version=$excelApp.Version; raw_export_sha256=$rawHash;
      checks=@('guide and gap tie-outs','observed Q3 guide','GBV edit propagation','zero versus missing cushion','fixed expectation benchmark','restored working inputs'); chart_counts=$chartCounts}
    $receipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $outputPath 'native_excel_checks.json')
    Write-Output ($receipt | ConvertTo-Json -Depth 5 -Compress)
} finally {
    if ($null -ne $excelBook) { $excelBook.Close($false) }
    if ($null -ne $excelApp) { $excelApp.Quit(); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($excelApp) }
}
