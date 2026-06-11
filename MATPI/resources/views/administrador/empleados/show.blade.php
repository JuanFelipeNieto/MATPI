@extends('layouts.admin')

@section('title', 'Detalles del Empleado | Matpi')

@section('content')
<div class="container mt-4">
    <h1>Detalles del Empleado</h1>

    <div class="card">
        <div class="card-body">
            <h4 class="card-title">{{ $empleado->usuario->Nombre_Completo }}</h4>
            <p><strong>ID:</strong> {{ $empleado->usuario->ID }}</p>
            <p><strong>Correo:</strong> {{ $empleado->usuario->Correo_Electronico }}</p>
            <p><strong>Teléfono:</strong> {{ $empleado->usuario->Telefono }}</p>
            <p><strong>Rol:</strong> {{ $empleado->usuario->Rol }}</p>
            <p><strong>Estado:</strong> {{ $empleado->usuario->Estado ? 'Activo' : 'Inactivo' }}</p>
            <p><strong>Dirección:</strong> {{ $empleado->usuario->Direccion }}</p>
            <p><strong>Fecha de Ingreso:</strong> {{ $empleado->usuario->Fecha_ingreso }}</p>
            <p><strong>Experiencia Laboral:</strong> {{ $empleado->usuario->Experiencia_Laboral }}</p>
            <p><strong>Fecha de Nacimiento:</strong> {{ $empleado->usuario->Fecha_Nacimiento }}</p>

            <hr>
            <p><strong>EPS:</strong> {{ $empleado->EPS }}</p>
            <p><strong>Tipo de Contrato:</strong> {{ $empleado->tipo_contrato }}</p>
            <p><strong>Contacto Emergencia:</strong> {{ $empleado->Contacto_Emergencia_Nombre }} 
                ({{ $empleado->Contacto_Emergencia_Parentesco }}) - {{ $empleado->Contacto_Emergencia_Numero }}</p>
            <p><strong>Fecha Terminación Contrato:</strong> {{ $empleado->Fecha_Terminacion_Contrato ?? 'N/A' }}</p>
        </div>
    </div>

    <a href="{{ route('administrador.empleados.index') }}" class="btn btn-secondary mt-3">Volver</a>
    <a href="{{ route('administrador.empleados.edit', $empleado->ID_Usr) }}" class="btn btn-warning mt-3">Editar</a>
</div>
@endsection
