@extends($layout)

@section('title', 'Detalle Materia Prima - Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/materiaprima.css') }}">

<div class="formulario-seccion">
    <h1>Detalle de Materia Prima</h1>

    <div class="detalle-card">
        <p><strong>Nombre:</strong> {{ $materiaPrima->nombre_materia_prima }}</p>
        <p><strong>Unidad de Medida:</strong> {{ $materiaPrima->unidad_medida }}</p>
        <p><strong>Cantidad Disponible:</strong> {{ $materiaPrima->cantidad }}</p>
        <p><strong>Fecha de Ingreso:</strong> {{ $materiaPrima->fecha_ingreso }}</p>
        <p><strong>Fecha de Vencimiento:</strong> {{ $materiaPrima->fecha_vencimiento ?? 'No definida' }}</p>
    </div>

    <div class="detalle-card">
        <h4>Productos que usan esta materia prima</h4>
        @if($materiaPrima->productos->isEmpty())
            <p>No hay productos asociados.</p>
        @else
            <ul class="detalle-lista">
                @foreach($materiaPrima->productos as $producto)
                    <li>
                        <span class="nombre">{{ $producto->nombre_producto }}</span>  
                        <span class="info">Cantidad usada: {{ $producto->pivot->cantidad_usada }}</span>
                    </li>
                @endforeach
            </ul>
        @endif
    </div>

    <div class="detalle-card">
        <h4>Proveedores que la suministran</h4>
        @if($materiaPrima->proveedores->isEmpty())
            <p>No hay proveedores registrados.</p>
        @else
            <ul class="detalle-lista">
                @foreach($materiaPrima->proveedores as $proveedor)
                    <li>
                        <span class="nombre">{{ $proveedor->nombre_proveedor }}</span>  
                        <span class="info">Precio: ${{ number_format($proveedor->pivot->precio_unitario, 0, ',', '.') }}</span>  
                        <span class="info">Fecha: {{ $proveedor->pivot->fecha_suministro }}</span>
                    </li>
                @endforeach
            </ul>
        @endif
    </div>

    <div class="detalle-actions">
        <a href="{{ route('materia_prima.index') }}" class="btn btn-cancelar">Volver</a>
        @if(Auth::user()->Rol === 'Administrador')
        @endif
    </div>
</div>
@endsection
