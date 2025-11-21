<?php

session_start();

// Si ya está logueado, redirigir a index.php automáticamente

if (isset($_SESSION['logueado']) && $_SESSION['logueado'] === true) {
    header('Location: index.php');
    exit;
 }

// Leer configuración desde config.php si se necesita conexión a la base de datos
require_once __DIR__ . '/config.php';

// Si no necesitas conexión a la base de datos para el login demo, puedes comentar o eliminar la siguiente sección:
 $conn = new mysqli($host, $user, $pass, $db);
 if ($conn->connect_error) {
     die('Error de conexión: ' . $conn->connect_error);
 }

$msg = '';
// Remover validación de login, permitir acceso directo
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['usuario'], $_POST['password'])) {
    $usuario = trim($_POST['usuario']);
    $password = trim($_POST['password']);
    // Usuario y contraseña fijos para demo
    $user_demo = getenv('APP_USER') ?: 'admin';
    $pass_demo = getenv('APP_PASS') ?: 'admin123';
    if ($usuario === $user_demo && $password === $pass_demo) {
        $_SESSION['logueado'] = true;
    // ...no loguear nada...
        header('Location: index.php');
        exit;
    } else {
        $msg = '<div class="error">Usuario o contraseña incorrectos</div>';
    // ...no loguear nada...
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Login - Demo App</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="app.css">
    <link rel="stylesheet" href="login.css">
    <script src="login.js"></script>
</head>
<body>
    <style>
    .shake {
        animation: shake 0.4s cubic-bezier(.36,.07,.19,.97) both;
    }
    @keyframes shake {
        10%, 90% { transform: translateX(-2px); }
        20%, 80% { transform: translateX(4px); }
        30%, 50%, 70% { transform: translateX(-8px); }
        40%, 60% { transform: translateX(8px); }
    }
    </style>
    <div class="login-box">
        <h2>Iniciar sesión</h2>
        <?= $msg ?>
        <form method="post" autocomplete="off">
            <input type="text" name="usuario" placeholder="Usuario" required autofocus>
            <input type="password" name="password" placeholder="Contraseña" required>
            <button type="submit">Entrar</button>
        </form>
    </div>
</body>
</html>
