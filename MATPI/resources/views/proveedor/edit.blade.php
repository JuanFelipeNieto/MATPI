@extends($layout)

@section('title', 'Editar Proveedor - Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/proveedores.css') }}">

<div class="formulario-seccion">
    <h1>Editar Proveedor</h1>

    @if($errors->any())
        <div class="alert alert-danger">
            <ul>
                @foreach($errors->all() as $error)
                    <li>{{ $error }}</li>
                @endforeach
            </ul>
        </div>
    @endif

    <form action="{{ route('proveedor.update', $proveedor) }}" method="POST">
        @csrf
        @method('PUT')

        <div class="form-group">
            <label>Nombre</label>
            <input type="text" name="nombre_proveedor" class="form-control" 
                   value="{{ old('nombre_proveedor', $proveedor->nombre_proveedor) }}" required>
        </div>

        <div class="form-group">
            <label>Correo Electrónico</label>
            <input type="email" name="correo_electronico" class="form-control" 
                   value="{{ old('correo_electronico', $proveedor->correo_electronico) }}">
        </div>

        <div class="form-group">
            <label>Teléfono</label>
            <input type="text" name="telefono" class="form-control" 
                   value="{{ old('telefono', $proveedor->telefono) }}" required>
        </div>

        <div class="form-group">
            <label>Dirección</label>
            <input type="text" name="direccion" class="form-control" 
                   value="{{ old('direccion', $proveedor->direccion) }}" required>
        </div>

        <div class="form-group">
            <label>Cantidad Suministrada</label>
            <input type="number" name="cantidad" class="form-control" 
                   value="{{ old('cantidad', $proveedor->cantidad) }}" required>
        </div>

        <div class="form-group">
            <label>Materia Prima</label>
            <select name="materia_prima_id" class="form-control" required>
                <option value="">Seleccione una materia prima</option>
                @foreach($materiasPrimas as $materia)
                    <option value="{{ $materia->id }}"
                        {{ old('materia_prima_id', optional($proveedor->materiasPrimas->first())->id) == $materia->id ? 'selected' : '' }}>
                        {{ $materia->nombre_materia_prima }}
                    </option>
                @endforeach
            </select>
        </div>

        <div class="form-group">
            <label>Precio Unitario</label>
            <input type="number" step="0.01" name="precio_unitario" class="form-control" 
                   value="{{ old('precio_unitario', optional($proveedor->materiasPrimas->first())->pivot->precio_unitario ?? '') }}" required>
        </div>

        <button type="submit" class="btn btn-primary">Actualizar</button>
        <a href="{{ route('proveedor.index') }}" class="btn btn-cancelar">Cancelar</a>
    </form>
</div>
@endsection
