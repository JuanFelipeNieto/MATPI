@extends($layout)

@section('title', 'Detalle del Pedido - Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/pedidos.css') }}">

<div class="formulario-seccion">
    <h1>Pedido #{{ $pedido->ID }}</h1>

    <p><strong>Fecha:</strong> {{ $pedido->Fecha }}</p>
    <p><strong>Mesa:</strong> {{ $pedido->Mesa ?? '-' }}</p>
    <p><strong>Número de Personas:</strong> {{ $pedido->Numero_Personas ?? '-' }}</p>
    <p><strong>Empleado:</strong> {{ $pedido->empleado->Nombre ?? 'Desconocido' }}</p>
    <p><strong>Cliente:</strong> {{ $pedido->cliente->Nombre ?? '-' }}</p>

    <h3>Productos</h3>
    <ul>
        @foreach($pedido->productos as $prod)
            <li>{{ $prod->nombre_producto }} x {{ $prod->pivot->cantidad }} (${{ $prod->Precio * $prod->pivot->cantidad }})</li>
        @endforeach
    </ul>

    <h3>Total: ${{ $pedido->Valor }}</h3>

    <div class="form-actions">
        <a href="{{ route('pedido.index') }}" class="btn btn-cancelar">Volver</a>
    </div>
</div>
@endsection
