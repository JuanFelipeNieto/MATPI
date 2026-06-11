@extends('layouts.admin')

@section('title', 'Editar Empleado | Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/empleados.css') }}">

<section class="formulario-seccion">
    <h1>Editar Empleado</h1>

    @if(session('success'))
        <div class="alert alert-success">{{ session('success') }}</div>
    @endif

    @if ($errors->any())
        <div class="alert alert-danger">
            <ul>
                @foreach ($errors->all() as $error)
                    <li>{{ $error }}</li>
                @endforeach
            </ul>
        </div>
    @endif

    <form action="{{ route('administrador.empleados.update', $empleado->ID_Usr) }}" method="POST">
        @csrf
        @method('PUT')

               <h4>Datos del Empleado</h4>

        @foreach (['ID','Nombre_Completo','Correo_Electronico','Telefono','Contraseña','Contraseña_confirmation','Direccion','Estado','Fecha_ingreso','Experiencia_Laboral','Fecha_Nacimiento'] as $campo)
            <div class="form-group">
                <label>{{ ucwords(str_replace('_',' ',$campo)) }}</label>
                @if(str_contains($campo,'Contraseña'))
                    <div class="input-group">
                        <input type="password" name="{{ $campo }}" class="form-control">
                        <button type="button" class="toggle-password">👁️</button>
                        <div class="input-help">Dejar vacío si no deseas cambiar la contraseña</div>
                    </div>
                @elseif($campo=='Estado')
                    <select name="Estado" class="form-control">
                        <option value="1" @if($empleado->usuario->Estado==1) selected @endif>Activo</option>
                        <option value="0" @if($empleado->usuario->Estado==0) selected @endif>Inactivo</option>
                    </select>
                @else
                    <input type="{{ in_array($campo,['Fecha_ingreso','Fecha_Nacimiento'])?'date':'text' }}" 
                           name="{{ $campo }}" class="form-control" 
                           value="{{ old($campo, $empleado->usuario->$campo) }}">
                @endif
            </div>
        @endforeach

        @foreach (['EPS','tipo_contrato','Contacto_Emergencia_Nombre','Contacto_Emergencia_Parentesco','Contacto_Emergencia_Numero','Fecha_Terminacion_Contrato'] as $campo)
            <div class="form-group">
                <label>{{ ucwords(str_replace('_',' ',$campo)) }}</label>
                @if($campo=='EPS')
                    <select name="EPS" class="form-control">
                        @foreach (['Nueva EPS','Sanitas','SURA','Salud Total','Compensar','Famisanar','Coosalud','Mutual Ser','SOS','Salud Mía','Aliansalud','Dusakawi','Salud Bolívar','Savia Salud','Cajacopi','Asmet Salud','Emssanar','Capital Salud'] as $eps)
                            <option value="{{ $eps }}" @if($empleado->EPS==$eps) selected @endif>{{ $eps }}</option>
                        @endforeach
                    </select>
                @elseif($campo=='tipo_contrato')
                    <select name="tipo_contrato" class="form-control">
                        @foreach(['Indefinido','Fijo','Servicios','Temporal'] as $tipo)
                            <option value="{{ $tipo }}" @if($empleado->tipo_contrato==$tipo) selected @endif>{{ $tipo }}</option>
                        @endforeach
                    </select>
                @else
                    <input type="{{ $campo=='Fecha_Terminacion_Contrato'?'date':'text' }}" 
                           name="{{ $campo }}" class="form-control" 
                           value="{{ old($campo, $empleado->$campo) }}">
                @endif
            </div>
        @endforeach

        <div class="perfil-actions">
            <button type="submit" class="btn btn-guardar">Actualizar</button>
            <a href="{{ route('administrador.empleados.index') }}" class="btn btn-cancelar">Cancelar</a>
        </div>
    </form>
</section>

<script>
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', () => {
            const input = button.previousElementSibling;
            input.type = input.type === 'password' ? 'text' : 'password';
        });
    });
</script>
@endsection
