# Script para crear un ZIP limpio del proyecto

# Ruta base del proyecto
$source = "c:\Users\AARON\PycharmProjects\servicio-tecnico-mvc"
$destination = "c:\Users\AARON\PycharmProjects\servicio-tecnico-mvc\servicio-tecnico-mvc-limpio.zip"

# Cerrar cualquier proceso que esté usando el archivo ZIP
Get-Process | Where-Object { $_.Path -like "*servicio-tecnico-mvc*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Si el archivo ZIP ya existe, eliminarlo
if (Test-Path $destination) {
    Remove-Item $destination -Force
}

# Crear un archivo temporal para la lista de archivos a incluir
$tempFile = [System.IO.Path]::GetTempFileName()

# Usar robocopy para listar archivos, excluyendo carpetas no deseadas
# Esto crea una lista de archivos que queremos incluir
$excludeDirs = @(
    'venv', 
    '__pycache__', 
    '.pytest_cache', 
    '.idea', 
    '.git',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '*.db',
    '.env',
    '*.log',
    '*.tmp',
    '*.bak',
    '*.swp',
    '*.swo',
    '*.swn',
    '*.swo',
    'node_modules',
    '.next',
    'dist',
    'build'
)

# Construir el comando robocopy
$robocopyCmd = "robocopy \"$source\" \"$source\" *.* /S /L /NJH /NJS /NC /NS /NP /XF *.pyc *.pyo *.pyd *.db *.log *.tmp *.bak *.swp *.swo *.swn *.swo /XD "
$robocopyCmd += ($excludeDirs -join ' ')
$robocopyCmd += " > \"$tempFile\""

# Ejecutar robocopy para obtener la lista de archivos
Invoke-Expression $robocopyCmd

# Leer la lista de archivos y crear el ZIP
Add-Type -Assembly 'System.IO.Compression.FileSystem'
$zip = [System.IO.Compression.ZipFile]::Open($destination, 'Create')

get-content $tempFile | ForEach-Object {
    $filePath = $_.Trim()
    if ($filePath -and (Test-Path $filePath -PathType Leaf)) {
        $relativePath = [System.IO.Path]::GetRelativePath($source, $filePath)
        $entryName = [System.IO.Path]::Combine([System.IO.Path]::GetDirectoryName($relativePath), [System.IO.Path]::GetFileName($filePath)).Replace('\', '/')
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $filePath, $entryName, [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
    }
}

# Cerrar el archivo ZIP
$zip.Dispose()

# Eliminar el archivo temporal
Remove-Item $tempFile -Force

Write-Host "Archivo ZIP creado exitosamente en: $destination" -ForegroundColor Green
