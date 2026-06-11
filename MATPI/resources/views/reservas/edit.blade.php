@extends($layout)

@section('title', 'Editar Reserva - Matpi')

@section('content')
<div class="formulario-seccion">
    <link rel="stylesheet" href="{{ asset('css/reservas.css') }}">

    <h1>Editar Reserva</h1>

    <form action="{{ route('reservas.update', $reserva->id) }}" method="POST">
        @csrf
        @method('PUT')

        <div class="form-group">
            <label for="id_cliente">ID del Cliente</label>
            <input type="number" name="id_cliente" id="id_cliente" value="{{ $reserva->ID_Usr }}" required>
            @error('id_cliente')
                <div class="alert alert-danger">{{ $message }}</div>
            @enderror
        </div>

        @php
            $fecha = date('Y-m-d', strtotime($reserva->Fecha));
            $hora = date('H:i', strtotime($reserva->Fecha));
        @endphp

        <div class="form-group">
            <label for="fecha">Fecha</label>
            <input type="date" name="fecha" id="fecha" value="{{ $fecha }}" min="{{ date('Y-m-d') }}" required>
            @error('fecha')
                <div class="alert alert-danger">{{ $message }}</div>
            @enderror
        </div>

        <div class="form-group">
            <label for="hora">Hora</label>
            <input type="time" name="hora" id="hora" value="{{ $hora }}" required>
            @error('hora')
                <div class="alert alert-danger">{{ $message }}</div>
            @enderror
        </div>

        <div class="form-group">
            <label for="estado">Estado</label>
            <select name="estado" id="estado" required>
                <option value="1" {{ $reserva->Estado ? 'selected' : '' }}>Activa</option>
                <option value="0" {{ !$reserva->Estado ? 'selected' : '' }}>Inactiva</option>
            </select>
            @error('estado')
                <div class="alert alert-danger">{{ $message }}</div>
            @enderror
        </div>

        <div class="form-group">
            <label for="observaciones">Observaciones</label>
            <textarea name="observaciones" id="observaciones" rows="3">{{ $reserva->Observaciones }}</textarea>
            @error('observaciones')
                <div class="alert alert-danger">{{ $message }}</div>
            @enderror
        </div>

        <button type="submit" class="btn">Actualizar Reserva</button>
        <a href="{{ route('reservas.index') }}" class="btn btn-cancelar">Cancelar</a>
    </form>
</div>
@endsection
