@extends($layout)

@section('title', 'Gestión de Proveedores - Matpi')

@section('content')
<div class="formulario-seccion">
<link rel="stylesheet" href="{{ asset('css/proveedores.css') }}">

    <h1>Proveedores</h1>

    @if(session('success'))
        <div class="alert alert-success">{{ session('success') }}</div>
    @endif

    <div class="cliente-buscador">
        <form method="GET" action="{{ route('proveedor.index') }}" class="proveedor-buscador">
            <input type="text" name="buscar" placeholder="Buscar por nombre o teléfono" value="{{ $buscar }}">
            <button type="submit" class="btn btn-guardar">Buscar</button>
        </form>
    </div>

    @if(Auth::user()->Rol === 'Administrador')
        <a href="{{ route('proveedor.create') }}" class="btn btn-primary">+ Nuevo Proveedor</a>
    @endif

    <table class="tabla-clientes">
        <thead>
            <tr>
                <th>ID</th>
                <th>Nombre Proveedor</th>
                <th>Teléfono</th>
                <th>Email</th>
                <th>Dirección</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            @forelse($proveedores as $proveedor)
                <tr>
                    <td>{{ $proveedor->id }}</td>
                    <td>{{ $proveedor->nombre_proveedor }}</td>
                    <td>{{ $proveedor->telefono }}</td>
                    <td>{{ $proveedor->correo_electronico }}</td>
                    <td>{{ $proveedor->direccion }}</td>
                    <td>
                        <a href="{{ route('proveedor.show', $proveedor) }}" class="btn btn-ver">Ver</a>
                        
                        @if(Auth::user()->Rol === 'Administrador' || Auth::user()->Rol === 'Empleado')
                            <a href="{{ route('proveedor.edit', $proveedor) }}" class="btn btn-editar">Editar</a>
                        @endif
                        
                        @if(Auth::user()->Rol === 'Administrador')
                            <form action="{{ route('proveedor.destroy', $proveedor) }}" method="POST" style="display:inline;">
                                @csrf
                                @method('DELETE')
                                <button type="submit" class="btn btn-danger" onclick="return confirm('¿Seguro que deseas eliminar este proveedor?')">Eliminar</button>
                            </form>
                        @endif
                    </td>
                </tr>
            @empty
                <tr>
                    <td colspan="6">No se encontraron proveedores.</td>
                </tr>
            @endforelse
        </tbody>
    </table>

    {{-- ✅ Paginación --}}
    <div class="paginacion">
        {{ $proveedores->links() }}
    </div>
</div>
@endsection
