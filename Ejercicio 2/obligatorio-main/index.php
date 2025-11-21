<?php


session_start();
if (!isset($_SESSION['logueado']) || !$_SESSION['logueado']) {
    header('Location: login.php');
    exit;
}

require_once 'config.php';

$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    die('<div class="error">Error de conexión a la base de datos: ' . $conn->connect_error . '</div>');
}

// Procesar acciones: agregar, editar, eliminar
$msg = '';

// Eliminar usuario
if (isset($_GET['delete'])) {
    $id = intval($_GET['delete']);
    $stmt = $conn->prepare("DELETE FROM usuarios WHERE id = ?");
    $stmt->bind_param('i', $id);
    if ($stmt->execute()) {
        $msg = '<div class="success">Usuario eliminado correctamente.</div>';
    } else {
        $msg = '<div class="error">Error al eliminar usuario.</div>';
    }
    $stmt->close();
}

// Editar usuario
if (isset($_POST['edit_id'], $_POST['edit_nombre'], $_POST['edit_email'], $_POST['edit_sueldo'], $_POST['edit_puesto'])) {
    $id = intval($_POST['edit_id']);
    $nombre = trim($_POST['edit_nombre']);
    $email = trim($_POST['edit_email']);
    $sueldo = floatval($_POST['edit_sueldo']);
    $puesto = trim($_POST['edit_puesto']);
    if ($nombre && filter_var($email, FILTER_VALIDATE_EMAIL) && $sueldo > 0 && $puesto) {
        $stmt = $conn->prepare("UPDATE usuarios SET nombre=?, email=?, sueldo=?, puesto=? WHERE id=?");
        $stmt->bind_param('ssdsi', $nombre, $email, $sueldo, $puesto, $id);
        if ($stmt->execute()) {
            $msg = '<div class="success">Usuario actualizado correctamente.</div>';
        } else {
            $msg = '<div class="error">Error al actualizar usuario.</div>';
        }
        $stmt->close();
    } else {
        $msg = '<div class="error">Datos inválidos para editar.</div>';
    }
}


// Agregar usuario
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['nombre'], $_POST['email'], $_POST['sueldo'], $_POST['puesto']) && !isset($_POST['edit_id'])) {
    $nombre = trim($_POST['nombre']);
    $email = trim($_POST['email']);
    $sueldo = floatval($_POST['sueldo']);
    $puesto = trim($_POST['puesto']);
    if ($nombre && filter_var($email, FILTER_VALIDATE_EMAIL) && $sueldo > 0 && $puesto) {
        $stmt = $conn->prepare("INSERT INTO usuarios (nombre, email, sueldo, puesto) VALUES (?, ?, ?, ?)");
        $stmt->bind_param('ssds', $nombre, $email, $sueldo, $puesto);
        if ($stmt->execute()) {
            $msg = '<div class="success">Usuario agregado correctamente.</div>';
        } else {
            $msg = '<div class="error">Error al agregar usuario.</div>';
        }
        $stmt->close();
    } else {
        $msg = '<div class="error">Completa todos los campos correctamente.</div>';
    }
}

$sql = 'SELECT id, nombre, email, sueldo, puesto FROM usuarios';
$result = $conn->query($sql);
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Usuarios - Demo App</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="app.css">
</head>
<body>
    <div class="container">
        <h1>👥 Usuarios registrados</h1>
        <button class="btn-nuevo" onclick="showModal()">Nuevo usuario</button>
        <?= $msg ?>
        <table>
            <tr><th>ID</th><th>Nombre</th><th>Email</th><th>Sueldo</th><th>Puesto</th><th>Acciones</th></tr>
            <?php if ($result && $result->num_rows > 0): ?>
                <?php while($row = $result->fetch_assoc()): ?>
                    <tr>
                        <td><?= htmlspecialchars($row['id']) ?></td>
                        <td><?= htmlspecialchars($row['nombre']) ?></td>
                        <td><?= htmlspecialchars($row['email']) ?></td>
                        <td><?= number_format($row['sueldo'], 2) ?></td>
                        <td><?= htmlspecialchars($row['puesto']) ?></td>
                        <td>
                            <button class="btn-edit" onclick="showEditModal(<?= $row['id'] ?>, '<?= htmlspecialchars($row['nombre'], ENT_QUOTES) ?>', '<?= htmlspecialchars($row['email'], ENT_QUOTES) ?>', '<?= htmlspecialchars($row['sueldo'], ENT_QUOTES) ?>', '<?= htmlspecialchars($row['puesto'], ENT_QUOTES) ?>')">Editar</button>
                            <a href="?delete=<?= $row['id'] ?>" class="btn-delete" onclick="return confirm('¿Seguro que deseas eliminar este usuario?');">Eliminar</a>
                        </td>
                    </tr>
                <?php endwhile; ?>
            <?php else: ?>
                <tr><td class="no-users" colspan="6">No hay usuarios</td></tr>
            <?php endif; ?>
        </table>
    </div>
    <div class="modal-bg" id="modal-bg">
        <div class="modal">
            <form class="form-add" method="post" autocomplete="off" onsubmit="return hideModal()">
                <input type="text" name="nombre" placeholder="Nombre" required>
                <input type="email" name="email" placeholder="Email" required>
                <input type="number" name="sueldo" placeholder="Sueldo" step="0.01" min="0" required>
                <input type="text" name="puesto" placeholder="Puesto de trabajo" required>
                <button type="submit">Agregar usuario</button>
                <button type="button" class="close-btn" onclick="hideModal()">Cancelar</button>
            </form>
        </div>
    </div>
    <style>
    .btn-delete {
        background: #c62828;
        color: #fff;
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 0.95rem;
        font-weight: 700;
        margin-right: 6px;
        cursor: pointer;
        transition: background 0.2s;
        text-decoration: none;
        display: inline-block;
    }
    .btn-delete:hover { background: #a31515; }
    .btn-edit {
        background: #fda085;
        color: #fff;
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 0.95rem;
        font-weight: 700;
        margin-right: 6px;
        cursor: pointer;
        transition: background 0.2s;
    }
    .btn-edit:hover { background: #f76d6d; }
    </style>
    <div class="modal-bg" id="edit-modal-bg">
        <div class="modal">
            <form class="form-add" method="post" autocomplete="off" onsubmit="return hideEditModal()">
                <input type="hidden" name="edit_id" id="edit_id">
                <input type="text" name="edit_nombre" id="edit_nombre" placeholder="Nombre" required>
                <input type="email" name="edit_email" id="edit_email" placeholder="Email" required>
                <input type="number" name="edit_sueldo" id="edit_sueldo" placeholder="Sueldo" step="0.01" min="0" required>
                <input type="text" name="edit_puesto" id="edit_puesto" placeholder="Puesto de trabajo" required>
                <button type="submit">Guardar cambios</button>
                <button type="button" class="close-btn" onclick="hideEditModal()">Cancelar</button>
            </form>
        </div>
    </div>
    <script>
    function showEditModal(id, nombre, email, sueldo, puesto) {
        document.getElementById('edit_id').value = id;
        document.getElementById('edit_nombre').value = nombre;
        document.getElementById('edit_email').value = email;
        document.getElementById('edit_sueldo').value = sueldo;
        document.getElementById('edit_puesto').value = puesto;
        document.getElementById('edit-modal-bg').style.display = 'block';
    }
    function hideEditModal() {
        document.getElementById('edit-modal-bg').style.display = 'none';
        return false;
    }
    function showModal() {
        document.getElementById('modal-bg').style.display = 'block';
    }
    function hideModal() {
        document.getElementById('modal-bg').style.display = 'none';
        return false;
    }
    </script>
    <script src="app.js"></script>
</body>
</html>
<?php $conn->close(); ?>
