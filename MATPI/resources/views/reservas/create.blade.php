@extends($layout)

@section('title', 'Crear Reserva - Matpi')

@section('content')
<div class="formulario-seccion">
    <link rel="stylesheet" href="{{ asset('css/reservas.css') }}">

    <h1>Crear Nueva Reserva</h1>

    <form action="{{ route('reservas.store') }}" method="POST">
        @csrf

        <div class="form-group">
            <label for="id_cliente">ID del Cliente</label>
            <input type="number" name="id_cliente" id="id_cliente" placeholder="Escribe el ID del cliente" required>
            @error('id_cliente')
                <div class="alert alert-danger">{{ $message }}</div>
            @enderror
        </div>

        <div class="form-group">
            <label for="fecha">Fecha</label>
            <input type="date" name="fecha" id="fecha" min="{{ date('Y-m-d') }}" required>
            @error('fecha')
                <div class="alert alert-danger">{{ $message }}</div>
            @enderror
        </div>

        <div class="form-group">
            <label for="hora">Hora</label>
            <input type="time" name="hora" id="hora" required>
            @error('hora')
                <div class="alert alert-danger">{{ $message }}</div>
            @enderror
        </div>

        <div class="form-group">
            <label for="estado">Estado</label>
            <select name="estado" id="estado" required>
                <option value="1">Activa</option>
                <option value="0">Inactiva</option>
            </select>
            @error('estado')
                <div class="alert alert-danger">{{ $message }}</div>
            @enderror
        </div>

        <div class="form-group">
            <label for="observaciones">Observaciones</label>
            <textarea name="observaciones" id="observaciones" rows="3"></textarea>
            @error('observaciones')
                <div class="alert alert-danger">{{ $message }}</div>
            @enderror
        </div>

        <button type="submit" class="btn">Guardar Reserva</button>
        <a href="{{ route('reservas.index') }}" class="btn btn-cancelar">Cancelar</a>
    </form>
</div>
@endsection
