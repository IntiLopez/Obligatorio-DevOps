<?php
// Buscar .env en el directorio anterior al del script
$envPath = dirname(__DIR__) . '/.env';
if (file_exists($envPath)) {
    // Lee claves en formato KEY=VALUE (sin comillas ni espacios alrededor)
    $vars = parse_ini_file($envPath, false, INI_SCANNER_RAW);
    foreach ($vars as $k => $v) {
        $_ENV[$k] = $v;
        putenv("$k=$v");
    }
}

$host = getenv('DB_HOST') ?: 'localhost';
$db   = getenv('DB_NAME') ?: 'test';
$user = getenv('DB_USER') ?: 'root';
$pass = getenv('DB_PASS') ?: 'root1234';

$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    die('Error de conexión: ' . $conn->connect_error);
}
?>

