@extends($layout)

@section('title', 'Editar Cliente - Matpi')

@section('content')
<div class="formulario-seccion">
    <link rel="stylesheet" href="{{ asset('css/perfil.css') }}">

    <h1>Editar Cliente</h1>

    @if ($errors->any())
        <div class="alert alert-danger">
            <ul>
                @foreach($errors->all() as $error)
                    <li>{{ $error }}</li>
                @endforeach
            </ul>
        </div>
    @endif

    <form action="{{ route('clientes.update', $cliente->ID) }}" method="POST">
        @csrf
        @method('PUT')

        <div class="form-group">
            <label for="ID">Número de Documento</label>
            <input type="number" name="ID" id="ID" value="{{ $cliente->ID }}" disabled>
        </div>

        <div class="form-group">
            <label for="Nombre_Completo">Nombre Completo</label>
            <input type="text" name="Nombre_Completo" id="Nombre_Completo" value="{{ old('Nombre_Completo', $cliente->Nombre_Completo) }}" required>
        </div>

        <div class="form-group">
            <label for="Telefono">Teléfono</label>
            <input type="text" name="Telefono" id="Telefono" value="{{ old('Telefono', $cliente->Telefono) }}" required>
        </div>

        <button type="submit" class="btn btn-guardar">Actualizar</button>
        <a href="{{ route('clientes.index') }}" class="btn btn-cancelar">Cancelar</a>
    </form>
</div>
@endsection
