@extends($layout)

@section('title', 'Detalle Proveedor - Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/proveedores.css') }}">

<div class="formulario-seccion">
    <h1>Detalle del Proveedor</h1>

    <div class="detalle-card">
        <p><strong>Nombre:</strong> {{ $proveedor->nombre_proveedor }}</p>
        <p><strong>Correo:</strong> {{ $proveedor->correo_electronico }}</p>
        <p><strong>Teléfono:</strong> {{ $proveedor->telefono }}</p>
        <p><strong>Dirección:</strong> {{ $proveedor->direccion }}</p>
        <p><strong>Cantidad Total Suministrada:</strong> {{ $proveedor->cantidad }}</p>
    </div>

    <div class="detalle-card">
        <h4>Materias Primas Suministradas</h4>
        @if($proveedor->materiasPrimas->isEmpty())
            <p>No ha suministrado materias primas.</p>
        @else
            <ul class="detalle-lista">
                @foreach($proveedor->materiasPrimas as $materia)
                    <li>
                        <span class="nombre">{{ $materia->nombre_materia_prima }}</span>
                        <span class="info">Precio: ${{ number_format($materia->pivot->precio_unitario, 0, ',', '.') }}</span>
                        <span class="info">Fecha: {{ $materia->pivot->fecha_suministro }}</span>
                    </li>
                @endforeach
            </ul>
        @endif
    </div>

    <div class="detalle-actions">
        <a href="{{ route('proveedor.index') }}" class="btn btn-cancelar">Volver</a>
        @if(Auth::user()->Rol === 'Administrador')
            </form>
        @endif
    </div>
</div>
@endsection
