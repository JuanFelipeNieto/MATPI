<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Reporte de Materias Primas</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            font-size: 12px;
            margin: 20px;
        }
        h1 {
            text-align: center;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            border: 1px solid #333;
            padding: 5px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        td {
            vertical-align: top;
        }
    </style>
</head>
<body>
    <h1>Reporte de Materias Primas</h1>

    <table>
        <thead>
            <tr>
                <th>Nombre</th>
                <th>Unidad de Medida</th>
                <th>Cantidad</th>
                <th>Fecha de Ingreso</th>
                <th>Fecha de Vencimiento</th>
            </tr>
        </thead>
        <tbody>
            @forelse($materiasPrimas as $mp)
            <tr>
                <td>{{ $mp->nombre_materia_prima }}</td>
                <td>{{ $mp->unidad_medida }}</td>
                <td>{{ $mp->cantidad }}</td>
                <td>{{ $mp->fecha_ingreso }}</td>
                <td>{{ $mp->fecha_vencimiento ?? '-' }}</td>
            </tr>
            @empty
            <tr>
                <td colspan="5" style="text-align:center;">No hay materias primas registradas.</td>
            </tr>
            @endforelse
        </tbody>
    </table>
</body>
</html>
