@extends($layout)

@section('title', 'Reservas - Matpi')

@section('content')
<div class="formulario-seccion">
    <link rel="stylesheet" href="{{ asset('css/reservas.css') }}">

    <h1>Reservas</h1>

    @if(session('success'))
        <div class="alert alert-success">{{ session('success') }}</div>
    @endif

    <div class="reserva-buscador">
        <form method="GET" action="{{ route('reservas.index') }}" class="form-busqueda">
            <input type="text" name="buscar" placeholder="Buscar por cliente o fecha" value="{{ $buscar ?? '' }}">
            <button type="submit" class="btn">Buscar</button>
        </form>

        <a href="{{ route('reservas.create') }}" class="btn">+ Nueva Reserva</a>
    </div>

    <div class="table-responsive">
        <table class="custom-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Cliente</th>
                    <th>Fecha</th>
                    <th>Estado</th>
                    <th>Observaciones</th>
                    <th>Registrado Por</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                @forelse($reservas as $reserva)
                <tr>
                    <td>{{ $reserva->id }}</td>
                    <td>{{ $reserva->cliente->Nombre_Completo ?? 'N/A' }}</td>
                    <td>{{ $reserva->Fecha }}</td>
                    <td>{{ $reserva->Estado ? 'Activa' : 'Inactiva' }}</td>
                    <td>{{ $reserva->Observaciones ?? 'N/A' }}</td>
                    <td>{{ $reserva->registrado_por }}</td>
                    <td class="acciones">
                        <a href="{{ route('reservas.edit', $reserva->id) }}" class="btn-editar">Editar</a>
                        <form action="{{ route('reservas.destroy', $reserva->id) }}" method="POST" style="display:inline;">
                            @csrf
                            @method('DELETE')
                            <button type="submit" class="btn-danger" onclick="return confirm('¿Seguro que deseas eliminar esta reserva?')">Eliminar</button>
                        </form>
                    </td>
                </tr>
                @empty
                <tr>
                    <td colspan="7">No hay reservas registradas.</td>
                </tr>
                @endforelse
            </tbody>
        </table>
    </div>
</div>
@endsection
