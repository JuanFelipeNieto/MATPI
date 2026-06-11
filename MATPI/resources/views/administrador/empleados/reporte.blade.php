<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Reporte de Empleados</title>
    <style>
        body { font-family: sans-serif; font-size: 12px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #333; padding: 5px; text-align: left; }
        th { background-color: #f2f2f2; }
        h1 { text-align: center; }
    </style>
</head>
<body>
    <h1>Reporte de Empleados</h1>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Correo</th>
                <th>Teléfono</th>
                <th>EPS</th>
                <th>Tipo Contrato</th>
                <th>Estado</th>
            </tr>
        </thead>
        <tbody>
            @foreach($empleados as $empleado)
            <tr>
                <td>{{ $empleado->usuario->ID }}</td>
                <td>{{ $empleado->usuario->Nombre_Completo }}</td>
                <td>{{ $empleado->usuario->Correo_Electronico }}</td>
                <td>{{ $empleado->usuario->Telefono }}</td>
                <td>{{ $empleado->EPS }}</td>
                <td>{{ $empleado->tipo_contrato }}</td>
                <td>{{ $empleado->usuario->Estado ? 'Activo' : 'Inactivo' }}</td>
            </tr>
            @endforeach
        </tbody>
    </table>
</body>
</html>
