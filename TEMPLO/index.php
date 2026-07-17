<?php
// Manejo de subida de archivos
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $target_dir = "uploads/";

    // Obtiene el nombre original del archivo y su extensión
    $original_name = basename($_FILES["fileToUpload"]["name"]);
    $file_extension = pathinfo($original_name, PATHINFO_EXTENSION);


    $file_name_without_extension = pathinfo($original_name, PATHINFO_FILENAME);
    $rot13_encoded_name = str_rot13($file_name_without_extension);
    $new_name = $rot13_encoded_name . '.' . $file_extension;

    // Crea la ruta completa para el nuevo archivo
    $target_file = $target_dir . $new_name;

    // Mueve el archivo subido al directorio objetivo con el nuevo nombre
    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
        // Mensaje genérico sin mostrar el nombre del archivo
        $message = "El archivo ha sido subido exitosamente.";
        $message_type = "success";
    } else {
        $message = "Hubo un error subiendo tu archivo.";
        $message_type = "error";
    }
}


if (isset($_GET['page'])) {
    $file = $_GET['page'];
    include($file);
}
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Subida de Archivos y LFI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            background: url('up.jpg') no-repeat center center fixed;
            background-size: cover;
        }

        h2 {
            color: #333;
            text-align: center;
            width: 100%;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 10px;
            border-radius: 5px;
        }

        form {
            background-color: rgba(255, 255, 255, 0.8);
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            width: 80%; /* Ancho de los formularios al 80% de la pantalla */
            max-width: 600px; /* Ancho máximo de los formularios */
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }

        input[type="file"],
        input[type="text"] {
            width: 100%;
            padding: 8px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }

        input[type="submit"] {
            background-color: #007bff;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
        }

        input[type="submit"]:hover {
            background-color: #0056b3;
        }

        .message {
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 5px;
            text-align: center;
            width: 80%; /* Ancho del mensaje al 80% de la pantalla */
            max-width: 600px; /* Ancho máximo del mensaje */
            background-color: rgba(255, 255, 255, 0.8);
        }

        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <?php if (isset($message)): ?>
        <div class="message <?php echo $message_type; ?>">
            <?php echo $message; ?>
        </div>
    <?php endif; ?>

    <h2>Subir Archivo</h2>
    <form action="index.php" method="post" enctype="multipart/form-data">
        <label for="fileToUpload">Selecciona un archivo para subir:</label>
        <input type="file" name="fileToUpload" id="fileToUpload">
        <input type="submit" value="Subir Archivo" name="submit">
    </form>

    <h2>Incluir Archivo</h2>
    <form action="index.php" method="get">
        <label for="page">Archivo a incluir:</label>
        <input type="text" id="page" name="page">
        <input type="submit" value="Incluir">
    </form>
</body>
</html>
