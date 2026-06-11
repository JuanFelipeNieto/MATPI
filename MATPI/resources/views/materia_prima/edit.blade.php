@extends($layout)

@section('title', 'Editar Materia Prima - Matpi')

@section('content')
<h1>Editar Materia Prima</h1>
    <link rel="stylesheet" href="{{ asset('css/clientes.css') }}">

@if($errors->any())
    <div class="alert alert-danger">
        <ul>
            @foreach($errors->all() as $error)
                <li>{{ $error }}</li>
            @endforeach
        </ul>
    </div>
@endif

<form action="{{ route('materia_prima.update', $materiaPrima) }}" method="POST">
    @csrf
    @method('PUT')

    <div class="form-group">
        <label>Nombre Materia Prima</label>
        <input type="text" name="nombre_materia_prima" class="form-control" value="{{ old('nombre_materia_prima', $materiaPrima->nombre_materia_prima) }}" required>
    </div>

    <div class="form-group">
        <label>Unidad de Medida</label>
        <input type="text" name="unidad_medida" class="form-control" value="{{ old('unidad_medida', $materiaPrima->unidad_medida) }}" required>
    </div>

    <div class="form-group">
        <label>Cantidad de unidades</label>
        <input type="number" name="cantidad" class="form-control" value="{{ old('cantidad', $materiaPrima->cantidad) }}" required>
    </div>

    <div class="form-group">
        <label>Fecha de Ingreso</label>
        <input type="datetime-local" name="fecha_ingreso" class="form-control" value="{{ old('fecha_ingreso', \Carbon\Carbon::parse($materiaPrima->fecha_ingreso)->format('Y-m-d\TH:i')) }}" required>
    </div>

    <div class="form-group">
        <label>Fecha de Vencimiento</label>
        <input type="date" name="fecha_vencimiento" class="form-control" value="{{ old('fecha_vencimiento', $materiaPrima->fecha_vencimiento) }}">
    </div>

    <button type="submit" class="btn btn-primary">Actualizar</button>
</form>
@endsection
