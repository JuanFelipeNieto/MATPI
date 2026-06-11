@extends($layout)

@section('title', 'Clientes - Matpi')

@section('content')
<div class="formulario-seccion">
    <link rel="stylesheet" href="{{ asset('css/clientes.css') }}">

    <h1>Clientes</h1>

    @if(session('success'))
        <div class="alert alert-success">{{ session('success') }}</div>
    @endif

    <div class="cliente-buscador">
       <form method="GET" action="{{ route('clientes.index') }}" class="form-busqueda">
    <input type="text" name="buscar" placeholder="Buscar por documento o nombre" value="{{ $buscar }}">
    <button type="submit" class="btn btn-guardar">Buscar</button>
</form>

        <a href="{{ route('clientes.create') }}" class="btn btn-guardar">+ Nuevo Cliente</a>
    </div>

    <div class="table-responsive">
        <table class="custom-table">
            <thead>
                <tr>
                    <th>Documento</th>
                    <th>Nombre Completo</th>
                    <th>Teléfono</th>
                    <th>Última Visita</th>
                    <th>Total Consumo</th>
                    <th>Fecha Registro</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                @forelse($clientes as $cliente)
                <tr>
                    <td>{{ $cliente->ID }}</td>
                    <td>{{ $cliente->Nombre_Completo }}</td>
                    <td>{{ $cliente->Telefono ?? 'N/A' }}</td>
                    <td>{{ $cliente->Ultima_Visita ?? 'N/A' }}</td>
                    <td>{{ $cliente->Total_Consumo }}</td>
                    <td>{{ $cliente->Fecha_Registro }}</td>
                    <td class="acciones">
                        <a href="{{ route('clientes.edit', $cliente->ID) }}" class="btn-editar">Editar</a>
                        <form action="{{ route('clientes.destroy', $cliente->ID) }}" method="POST" style="display:inline;">
                            @csrf
                            @method('DELETE')
                            <button type="submit" class="btn-danger" onclick="return confirm('¿Seguro que deseas eliminar este cliente?')">Eliminar</button>
                        </form>
                    </td>
                </tr>
                @empty
                <tr>
                    <td colspan="7">No hay clientes registrados.</td>
                </tr>
                @endforelse
            </tbody>
        </table>
    </div>

   

</div>
@endsection
