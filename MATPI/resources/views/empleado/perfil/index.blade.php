@extends('layouts.empleado')

@section('title', 'Perfil Empleado | Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/perfil.css') }}">
<section class="formulario-seccion">
    <h1>Mi Perfil</h1>

    <div class="perfil-info">
        <div class="perfil-card">
            <strong>Nombre</strong>
            <p>{{ $empleado->usuario->Nombre_Completo }}</p>
        </div>
        <div class="perfil-card">
            <strong>Correo</strong>
            <p>{{ $empleado->usuario->Correo_Electronico }}</p>
        </div>
        <div class="perfil-card">
            <strong>Teléfono</strong>
            <p>{{ $empleado->usuario->Telefono }}</p>
        </div>
        <div class="perfil-card">
            <strong>Dirección</strong>
            <p>{{ $empleado->usuario->Direccion }}</p>
        </div>
        <div class="perfil-card">
            <strong>Fecha de Nacimiento</strong>
            <p>{{ $empleado->usuario->Fecha_Nacimiento }}</p>
        </div>
          <div class="perfil-card">
            <strong>Experiencia Laboral</strong>
            <p>{{ $empleado->usuario->Experiencia_Laboral }}</p>
        </div>
        <div class="perfil-card">
            <strong>EPS</strong>
            <p>{{ $empleado->EPS }}</p>
        </div>
        <div class="perfil-card">
            <strong>Tipo de Contrato</strong>
            <p>{{ $empleado->tipo_contrato }}</p>
        </div>
    </div>
</section>
@endsection
