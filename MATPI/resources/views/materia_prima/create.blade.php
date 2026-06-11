@extends($layout)

@section('title', 'Crear Materia Prima - Matpi')

@section('content')
<h1>Crear Materia Prima</h1>
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

<form action="{{ route('materia_prima.store') }}" method="POST">
    @csrf

    <div class="form-group">
        <label>Nombre Materia Prima</label>
        <input type="text" name="nombre_materia_prima" class="form-control" value="{{ old('nombre_materia_prima') }}" required>
    </div>

    <div class="form-group">
        <label>Unidad de Medida</label>
        <input type="text" name="unidad_medida" class="form-control" value="{{ old('unidad_medida') }}" required>
    </div>

    <div class="form-group">
        <label>Cantidad de unidades</label>
        <input type="number" name="cantidad" class="form-control" value="{{ old('cantidad', 0) }}" required>
    </div>

    <div class="form-group">
    <label>Fecha de Ingreso</label>
    <input type="datetime-local" 
           name="fecha_ingreso" 
           class="form-control" 
           value="{{ old('fecha_ingreso', now()->format('Y-m-d\TH:i')) }}" 
           required>
</div>


    <div class="form-group">
        <label>Fecha de Vencimiento</label>
        <input type="date" name="fecha_vencimiento" class="form-control" value="{{ old('fecha_vencimiento') }}">
    </div>

    <button type="submit" class="btn btn-primary">Guardar</button>
</form>
@endsection
