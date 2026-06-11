@extends($layout)

@section('title', 'Crear Proveedor - Matpi')

@section('content')
<h1>Crear Proveedor</h1>
<link rel="stylesheet" href="{{ asset('css/proveedores.css') }}">

@if($errors->any())
    <div class="alert alert-danger">
        <ul>
            @foreach($errors->all() as $error)
                <li>{{ $error }}</li>
            @endforeach
        </ul>
    </div>
@endif

<form action="{{ route('proveedor.store') }}" method="POST">
    @csrf

    <div class="form-group">
        <label>Nombre Proveedor</label>
        <input type="text" name="nombre_proveedor" class="form-control" value="{{ old('nombre_proveedor') }}" required>
    </div>

    <div class="form-group">
        <label>Dirección</label>
        <input type="text" name="direccion" class="form-control" value="{{ old('direccion') }}" required>
    </div>

    <div class="form-group">
        <label>Correo Electrónico</label>
        <input type="email" name="correo_electronico" class="form-control" value="{{ old('correo_electronico') }}">
    </div>

    <div class="form-group">
        <label>Teléfono</label>
        <input type="text" name="telefono" class="form-control" value="{{ old('telefono') }}" required>
    </div>

    <div class="form-group">
        <label>Materia Prima</label>
        <select name="materia_prima_id" class="form-control" required>
            <option value="">Seleccione una materia prima</option>
            @foreach($materiasPrimas as $materia)
                <option value="{{ $materia->id }}" {{ old('materia_prima_id') == $materia->id ? 'selected' : '' }}>
                    {{ $materia->nombre_materia_prima }} (Stock actual: {{ $materia->cantidad }} {{ $materia->unidad_medida }})
                </option>
            @endforeach
        </select>
    </div>

    <div class="form-group">
        <label>Precio Unitario</label>
        <input type="number" step="0.01" name="precio_unitario" class="form-control" value="{{ old('precio_unitario') }}" required>
    </div>

    <button type="submit" class="btn btn-primary">Guardar</button>
    <a href="{{ route('proveedor.index') }}" class="btn btn-secondary">Cancelar</a>
</form>
@endsection
