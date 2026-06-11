@extends($layout)

@section('title', 'Productos - Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/productos.css') }}">

<div class="formulario-seccion">
    <h1>Productos</h1>

    @if(session('success'))
        <div class="alert alert-success">{{ session('success') }}</div>
    @endif

    <form method="GET" action="{{ route('producto.index') }}" class="form-busqueda">
        <input type="text" name="search" placeholder="Buscar producto o categoría"
               value="{{ $search ?? '' }}">
        <button type="submit">Buscar</button>
    </form>

    {{-- Botón crear (solo Admin) --}}
    @if(Auth::user()->Rol === 'Administrador')
        <div class="acciones-top" style="margin-bottom: 15px;">
            <a href="{{ route('producto.create') }}" class="btn">+ Nuevo Producto</a>
        </div>
    @endif

    {{-- Tabla de productos --}}
    <div class="table-responsive">
        <table class="custom-table table-productos">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Imagen</th>
                    <th>Nombre</th>
                    <th>Categoría</th>
                    <th>Cantidad Disponible</th>
                    <th>Valor</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                @forelse($productos as $producto)
                    <tr>
                        <td>{{ $producto->id }}</td>
                        <td>
                            @if($producto->imagen)
                                {{-- Usa Storage::url() para manejar ambos casos --}}
                                <img src="{{ Storage::url($producto->imagen) }}" 
                                     alt="imagen" class="producto-imagen">
                            @else
                                <span>Sin imagen</span>
                            @endif
                        </td>
                        <td>{{ $producto->nombre_producto }}</td>
                        <td>{{ $producto->categoria }}</td>
                        <td>{{ $producto->cantidad }}</td>
                        <td>${{ number_format($producto->valor, 0, ',', '.') }}</td>
                        <td class="acciones">
                            {{-- Botón Ver (todos los roles) --}}
                            <a href="{{ route('producto.show', $producto) }}" class="btn-editar">Ver</a>

                            {{-- Solo Admin puede Editar y Eliminar --}}
                            @if(Auth::user()->Rol === 'Administrador')
                                <a href="{{ route('producto.edit', $producto) }}" class="btn-editar">Editar</a>
                                <form action="{{ route('producto.destroy', $producto) }}" method="POST" style="display:inline;">
                                    @csrf
                                    @method('DELETE')
                                    <button type="submit" class="btn-danger" onclick="return confirm('¿Eliminar producto?')">Eliminar</button>
                                </form>
                            @endif
                        </td>
                    </tr>
                @empty
                    <tr>
                        <td colspan="7">No se encontraron productos.</td>
                    </tr>
                @endforelse
            </tbody>
        </table>
    </div>
</div>
@endsection
