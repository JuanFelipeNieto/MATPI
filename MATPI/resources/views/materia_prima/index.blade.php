@extends($layout)

@section('title', 'Materias Primas - Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/materiaprima.css') }}">

<section class="formulario-seccion">
    <h1>Materia Prima</h1>

    @if(session('success'))
        <div class="alert alert-success">{{ session('success') }}</div>
    @endif

    @if(session('error'))
        <div class="alert alert-danger">{{ session('error') }}</div>
    @endif

    {{-- Contenedor de buscador + botones --}}
    <div class="buscador-nuevo" style="display:flex; justify-content: space-between; align-items:center; margin-bottom:20px; flex-wrap: wrap;">
        <form method="GET" action="{{ route('materia_prima.index') }}" class="form-busqueda" style="margin:0;">
            <input type="text" name="buscar" placeholder="Buscar por nombre" value="{{ $buscar ?? '' }}">
            <button type="submit" class="btn btn-guardar">Buscar</button>
        </form>

        <div style="display:flex; gap:10px; flex-wrap: wrap; margin-top:5px;">
            @if(Auth::user()->Rol === 'Administrador')
                <a href="{{ route('materia_prima.create') }}" class="btn btn-guardar">+ Nueva Materia Prima</a>
            @endif
          <a href="{{ route('materia_prima.reporte', ['buscar' => $buscar ?? '']) }}" class="btn btn-guardar">
    📄 Descargar Reporte PDF
</a>

        </div>
    </div>

    <div class="table-responsive">
        <table class="custom-table">
            <thead>
                <tr>
                    <th>Nombre</th>
                    <th>Unidad de Medida</th>
                    <th>Cantidad de unidades</th>
                    <th>Fecha Ingreso</th>
                    <th>Fecha Vencimiento</th>
                    <th>Acciones</th>
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
                    <td class="acciones">
                        <a href="{{ route('materia_prima.show', $mp) }}" class="btn btn-editar">Ver</a>
                        @if(Auth::user()->Rol === 'Administrador')
                            <a href="{{ route('materia_prima.edit', $mp) }}" class="btn btn-editar">Editar</a>
                            <form action="{{ route('materia_prima.destroy', $mp) }}" method="POST" onsubmit="return confirm('¿Seguro que quieres eliminar esta materia prima?');" style="display:inline;">
                                @csrf
                                @method('DELETE')
                                <button type="submit" class="btn btn-danger">Eliminar</button>
                            </form>
                        @endif
                    </td>
                </tr>
                @empty
                <tr>
                    <td colspan="6" class="text-center">No hay materias primas registradas.</td>
                </tr>
                @endforelse
            </tbody>
        </table>
    </div>

    <div class="perfil-actions">
        {{ $materiasPrimas->links() }}
    </div>
</section>
@endsection
