@extends($layout)

@section('title', 'Detalle Producto - Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/productos.css') }}">

<div class="formulario-seccion">
    <h1>Detalle del Producto</h1>

    <div style="text-align: center; margin-bottom: 20px;">
        @if($producto->imagen)
            <img src="{{ asset('storage/' . $producto->imagen) }}" alt="Imagen" class="producto-imagen" style="max-width: 250px;">
        @else
            <span>Sin imagen</span>
        @endif
    </div>
<div  class="detalle-card">
    <p><strong>Nombre:</strong> {{ $producto->nombre_producto }}</p>
    <p><strong>Descripción:</strong> {{ $producto->descripcion ?? 'No tiene' }}</p>
    <p><strong>Categoría:</strong> {{ $producto->categoria }}</p>
    <p><strong>Valor:</strong> ${{ number_format($producto->valor, 0, ',', '.') }}</p>
    <p><strong>Cantidad Disponible:</strong> {{ $producto->cantidad }}</p>

    <h3>Materias Primas</h3>
    <ul>
        @forelse($producto->materiasPrimas as $materia)
            <li>
                {{ $materia->nombre_materia_prima }} 
                ({{ $materia->pivot->cantidad_usada }} {{ $materia->unidad_medida }})
            </li>
        @empty
            <li>No tiene materias primas asignadas</li>
        @endforelse
    </ul>
</div>
    <div class="form-actions">
        <a href="{{ route('producto.index') }}" class="btn btn-cancelar">Volver</a>
        <a href="{{ route('producto.edit', $producto->id) }}" class="btn btn-crear">Editar</a>
    </div>
</div>
@endsection
