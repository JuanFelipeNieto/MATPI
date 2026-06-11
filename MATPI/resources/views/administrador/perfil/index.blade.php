@extends('layouts.admin')

@section('title', 'Perfil Administrador | Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/perfil.css') }}">
<section class="formulario-seccion">
    <h1>Mi Perfil</h1>

    @if(session('success'))
        <div class="alert alert-success">{{ session('success') }}</div>
    @endif

    <div class="perfil-info">
        <div class="perfil-card">
            <strong>Nombre</strong>
            <p>{{ $administrador->usuario->Nombre_Completo }}</p>
        </div>
        <div class="perfil-card">
            <strong>Correo</strong>
            <p>{{ $administrador->usuario->Correo_Electronico }}</p>
        </div>
        <div class="perfil-card">
            <strong>Teléfono</strong>
            <p>{{ $administrador->usuario->Telefono }}</p>
        </div>
        <div class="perfil-card">
            <strong>Dirección</strong>
            <p>{{ $administrador->usuario->Direccion }}</p>
        </div>
        <div class="perfil-card">
            <strong>Fecha de Nacimiento</strong>
            <p>{{ $administrador->usuario->Fecha_Nacimiento }}</p>
        </div>
        <div class="perfil-card">
            <strong>Experiencia Laboral</strong>
            <p>{{ $administrador->usuario->Experiencia_Laboral }}</p>
        </div>
        <div class="perfil-card">
            <strong>Formación Educativa</strong>
            <p>{{ $administrador->Formacion_Educativa }}</p>
        </div>
    </div>

    <div class="perfil-actions">
        <a href="{{ route('administrador.perfil.editar') }}" class="btn btn-editar">Editar Perfil</a>
    </div>
</section>
@endsection
