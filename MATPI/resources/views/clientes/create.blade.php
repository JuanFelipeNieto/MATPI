@extends($layout)

@section('title', 'Crear Cliente - Matpi')

@section('content')
<div class="formulario-seccion">
    <link rel="stylesheet" href="{{ asset('css/empleados.css') }}">

    <h1>Registrar Cliente</h1>

    @if ($errors->any())
        <div class="alert alert-danger">
            <ul>
                @foreach($errors->all() as $error)
                    <li>{{ $error }}</li>
                @endforeach
            </ul>
        </div>
    @endif

    <form action="{{ route('clientes.store') }}" method="POST">
        @csrf
        <div class="form-group">
            <label for="ID">Número de Documento</label>
            <input type="number" name="ID" id="ID" value="{{ old('ID') }}" required min="1000000000" max="9999999999" placeholder="Ingrese documento">
        </div>

        <div class="form-group">
            <label for="Nombre_Completo">Nombre Completo</label>
            <input type="text" name="Nombre_Completo" id="Nombre_Completo" value="{{ old('Nombre_Completo') }}" required placeholder="Ingrese nombre completo">
        </div>

        <div class="form-group">
            <label for="Telefono">Teléfono</label>
            <input type="text" name="Telefono" id="Telefono" value="{{ old('Telefono') }}" required placeholder="Ingrese teléfono">
        </div>

        <button type="submit" class="btn btn-guardar">Guardar</button>
        <a href="{{ route('clientes.index') }}" class="btn btn-cancelar">Cancelar</a>
    </form>
</div>
@endsection
