@extends($layout)

@section('title', 'Editar Pedido - Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/pedidos.css') }}">

<div class="formulario-seccion">
    <h1>Editar Pedido</h1>

    <form action="{{ route('pedido.update', $pedido) }}" method="POST">
        @csrf
        @method('PUT')

        <label>Fecha:</label>
        <input type="datetime-local" name="Fecha" value="{{ $pedido->Fecha->format('Y-m-d\TH:i') }}" required>

        <label>Empleado:</label>
        <select name="ID_Usr" required>
            @foreach($empleados as $emp)
                <option value="{{ $emp->ID_Usr }}" @if($pedido->ID_Usr == $emp->ID_Usr) selected @endif>{{ $emp->Nombre_Completo }}</option>
            @endforeach
        </select>

        <label>Cliente:</label>
        <select name="ID_Cliente">
            <option value="">Ninguno</option>
            @foreach($clientes as $cli)
                <option value="{{ $cli->ID }}" @if($pedido->ID_Cliente == $cli->ID) selected @endif>{{ $cli->Nombre_Completo }}</option>
            @endforeach
        </select>

        <label>Reserva:</label>
        <select name="ID_Reserva">
            <option value="">Ninguna</option>
            @foreach($reservas as $res)
                <option value="{{ $res->id }}" @if($pedido->ID_Reserva == $res->id) selected @endif>{{ $res->id }} - {{ $res->Fecha }}</option>
            @endforeach
        </select>

        <label>Mesa:</label>
        <input type="number" name="Mesa" value="{{ $pedido->Mesa }}">

        <label>Número de personas:</label>
        <input type="number" name="Numero_Personas" value="{{ $pedido->Numero_Personas }}">

        <label>Valor:</label>
        <input type="number" name="Valor" value="{{ $pedido->Valor }}" required>

        <label>Estado:</label>
        <select name="Estado" required>
            <option value="1" @if($pedido->Estado) selected @endif>Activo</option>
            <option value="0" @if(!$pedido->Estado) selected @endif>Inactivo</option>
        </select>

        <label>Productos:</label>
        @foreach($productos as $prod)
            <div>
                <input type="checkbox" name="productos[{{ $prod->ID }}][id]" value="{{ $prod->ID }}"
                       @if($pedido->productos->contains($prod->ID)) checked @endif>
                {{ $prod->Nombre_Producto }}
                <input type="number" name="productos[{{ $prod->ID }}][cantidad]"
                       value="{{ $pedido->productos->contains($prod->ID) ? $pedido->productos->find($prod->ID)->pivot->cantidad : 1 }}"
                       min="1">
            </div>
        @endforeach

        <button type="submit" class="btn">Actualizar Pedido</button>
    </form>
</div>
@endsection
