@extends($layout)

@section('title', 'Empleados | Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/empleados.css') }}">

<section class="formulario-seccion">
    <h1>Empleados</h1>

    @if(session('success'))
        <div class="alert alert-success">{{ session('success') }}</div>
    @endif

    @if(session('error'))
        <div class="alert alert-danger">{{ session('error') }}</div>
    @endif

    {{-- Contenedor de buscador + botones --}}
    <div class="buscador-nuevo" style="display:flex; justify-content: space-between; align-items:center; margin-bottom:20px; flex-wrap: wrap;">
        <form action="{{ route('administrador.empleados.index') }}" method="GET" class="form-busqueda" style="margin:0;">
            <input type="text" name="buscar" placeholder="Buscar por ID o Nombre" value="{{ $buscar ?? '' }}">
            <button type="submit">Buscar</button>
        </form>

        <div style="display:flex; gap:10px; flex-wrap: wrap; margin-top:5px;">
            <a href="{{ route('administrador.empleados.create') }}" class="btn btn-guardar">+ Nuevo Empleado</a>
            <a href="{{ route('administrador.empleados.reporte', ['buscar' => $buscar ?? '']) }}" class="btn btn-guardar">
                📄 Descargar Reporte PDF
            </a>
        </div>
    </div>

    <div class="table-responsive">
        <table class="custom-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Correo</th>
                    <th>Teléfono</th>
                    <th>EPS</th>
                    <th>Tipo Contrato</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                @forelse($empleados as $empleado)
                <tr>
                    <td>{{ $empleado->usuario->ID }}</td>
                    <td>{{ $empleado->usuario->Nombre_Completo }}</td>
                    <td>{{ $empleado->usuario->Correo_Electronico }}</td>
                    <td>{{ $empleado->usuario->Telefono }}</td>
                    <td>{{ $empleado->EPS }}</td>
                    <td>{{ $empleado->tipo_contrato }}</td>
                    <td>{{ $empleado->usuario->Estado ? 'Activo' : 'Inactivo' }}</td>
                    <td class="acciones">
                        <a href="{{ route('administrador.empleados.edit', $empleado) }}" class="btn btn-editar">Editar</a>
                        <form action="{{ route('administrador.empleados.destroy', $empleado) }}" method="POST" onsubmit="return confirm('¿Seguro que deseas eliminar este empleado?');" style="display:inline;">
                            @csrf
                            @method('DELETE')
                            <button type="submit" class="btn btn-danger">Eliminar</button>
                        </form>
                    </td>
                </tr>
                @empty
                <tr>
                    <td colspan="8" class="text-center">No hay empleados registrados.</td>
                </tr>
                @endforelse
            </tbody>
        </table>
    </div>

    <div class="perfil-actions">
        {{ $empleados->links() }}
    </div>
</section>
@endsection
