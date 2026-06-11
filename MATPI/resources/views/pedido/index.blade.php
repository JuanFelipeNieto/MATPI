@extends($layout)

@section('title', 'Pedidos - Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/pedidos.css') }}">

<div class="formulario-seccion">
    <h1>Pedidos</h1>

    <a href="{{ route('pedido.create') }}" class="btn btn-crear">Nuevo Pedido</a>

    <table class="tabla-pedidos">
        <thead>
            <tr>
                <th>ID</th>
                <th>Fecha</th>
                <th>Mesa</th>
                <th>Número de Personas</th>
                <th>Productos</th>
                <th>Total</th>
                <th>Estado</th>
            </tr>
        </thead>
        <tbody>
            @foreach($pedidos as $pedido)
            <tr>
                <td>{{ $pedido->ID }}</td>
                <td>{{ $pedido->Fecha }}</td>
                <td>{{ $pedido->Mesa ?? '-' }}</td>
                <td>{{ $pedido->Numero_Personas ?? '-' }}</td>
                <td>
                    <ul>
                        @foreach($pedido->productos as $prod)
                            <li>{{ $prod->nombre_producto }} x {{ $prod->pivot->cantidad }}</li>
                        @endforeach
                    </ul>
                </td>
                <td>${{ $pedido->Valor }}</td>
                <td>{{ $pedido->Estado ? 'Activo' : 'Completado' }}</td>
            </tr>
            @endforeach
        </tbody>
    </table>
</div>
@endsection
