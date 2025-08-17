# Script simplificado para crear un ZIP limpio del proyecto

# Ruta base del proyecto
$source = "c:\Users\AARON\PycharmProjects\servicio-tecnico-mvc"
$destination = "c:\Users\AARON\PycharmProjects\servicio-tecnico-mvc\servicio-tecnico-mvc-limpio.zip"

# Si el archivo ZIP ya existe, eliminarlo
if (Test-Path $destination) {
    Remove-Item $destination -Force
}

# Crear un archivo ZIP temporal
$tempZip = [System.IO.Path]::GetTempFileName()

# Usar Compress-Archive para crear el ZIP inicial
$filesToInclude = Get-ChildItem -Path $source -Recurse -File | 
    Where-Object {
        $exclude = $false
        $excludeDirs = @('venv', '__pycache__', '.pytest_cache', '.idea', '.git', 'node_modules', '.next', 'dist', 'build')
        $excludeExts = @('.pyc', '.pyo', '.pyd', '.db', '.log', '.tmp', '.bak', '.swp', '.swo', '.swn')
        
        # Verificar si el archivo está en una carpeta excluida
        foreach ($dir in $excludeDirs) {
            if ($_.FullName -match [regex]::Escape($dir)) {
                $exclude = $true
                break
            }
        }
        
        # Verificar si el archivo tiene una extensión excluida
        if (-not $exclude) {
            foreach ($ext in $excludeExts) {
                if ($_.Name.EndsWith($ext)) {
                    $exclude = $true
                    break
                }
            }
        }
        
        -not $exclude
    }

# Crear el ZIP con los archivos filtrados
Add-Type -Assembly 'System.IO.Compression.FileSystem'
$zip = [System.IO.Compression.ZipFile]::Open($tempZip, 'Create')

foreach ($file in $filesToInclude) {
    $relativePath = [System.IO.Path]::GetRelativePath($source, $file.FullName)
    $entryName = [System.IO.Path]::Combine([System.IO.Path]::GetDirectoryName($relativePath), [System.IO.Path]::GetFileName($file.FullName)).Replace('\', '/')
    $entry = [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $file.FullName, $entryName, [System.IO.Compression.CompressionLevel]::Optimal)
}

# Cerrar el archivo ZIP
$zip.Dispose()

# Mover el archivo temporal a la ubicación final
Move-Item -Path $tempZip -Destination $destination -Force

Write-Host "Archivo ZIP creado exitosamente en: $destination" -ForegroundColor Green
