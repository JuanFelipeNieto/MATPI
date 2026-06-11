@extends('layouts.admin')

@section('title', 'Editar Perfil Administrador | Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/perfil.css') }}">

<section class="formulario-seccion">
    <h1>Editar Perfil</h1>

    @if($errors->any())
        <div class="alert alert-danger">
            <ul>
                @foreach($errors->all() as $error)
                    <li>{{ $error }}</li>
                @endforeach
            </ul>
        </div>
    @endif

    <form action="{{ route('administrador.perfil.update') }}" method="POST">
        @csrf
        @method('PUT')

        <div class="form-group">
            <label for="Nombre_Completo">Nombre completo</label>
            <input type="text" name="Nombre_Completo" id="Nombre_Completo" value="{{ old('Nombre_Completo', $administrador->usuario->Nombre_Completo) }}" required>
        </div>

        <div class="form-group">
            <label for="Correo_Electronico">Correo electrónico</label>
            <input type="email" name="Correo_Electronico" id="Correo_Electronico" value="{{ old('Correo_Electronico', $administrador->usuario->Correo_Electronico) }}" required>
        </div>

        <div class="form-group">
            <label for="Telefono">Teléfono</label>
            <input type="text" name="Telefono" id="Telefono" value="{{ old('Telefono', $administrador->usuario->Telefono) }}" required>
        </div>

        <div class="form-group">
            <label for="Direccion">Dirección</label>
            <input type="text" name="Direccion" id="Direccion" value="{{ old('Direccion', $administrador->usuario->Direccion) }}" required>
        </div>

       <div class="form-group">
    <label for="Fecha_Nacimiento">Fecha de Nacimiento</label>
    <input type="date" 
           name="Fecha_Nacimiento" 
           id="Fecha_Nacimiento" 
           value="{{ old('Fecha_Nacimiento', $administrador->usuario->Fecha_Nacimiento) }}"
           required
           max="{{ \Carbon\Carbon::now()->subYears(18)->format('Y-m-d') }}">
</div>

        <div class="form-group">
            <label for="Experiencia_Laboral">Experiencia Laboral</label>
            <textarea name="Experiencia_Laboral" id="Experiencia_Laboral" required>{{ old('Experiencia_Laboral', $administrador->usuario->Experiencia_Laboral) }}</textarea>
        </div>

        <div class="form-group">
            <label for="Formacion_Educativa">Formación Educativa</label>
            <input type="text" name="Formacion_Educativa" id="Formacion_Educativa" value="{{ old('Formacion_Educativa', $administrador->Formacion_Educativa) }}" required>
        </div>

        <div class="form-group">
            <a href="{{ route('administrador.perfil.password.edit') }}" class="btn btn-editar">Cambiar contraseña</a>
        </div>

        <button type="submit" class="btn btn-guardar">Guardar Cambios</button>
    </form>
</section>
@endsection
