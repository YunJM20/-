param([string]$src, [string]$outdir, [string]$slides = "")
New-Item -ItemType Directory -Force $outdir | Out-Null
$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Open($src, $true, $false, $false)   # ReadOnly, Untitled=false, WithWindow=false
$n = $pres.Slides.Count
if ($slides -eq "") { $idx = 1..$n } else { $idx = $slides.Split(",") | ForEach-Object { [int]$_ } }
foreach ($i in $idx) {
    if ($i -le $n) { $pres.Slides.Item($i).Export((Join-Path $outdir ("s{0:D2}.png" -f $i)), "PNG", 1600, 900) }
}
$pres.Close()
$ppt.Quit()
"exported " + $idx.Count + " of " + $n
