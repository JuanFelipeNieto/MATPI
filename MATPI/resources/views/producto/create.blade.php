@extends($layout)

@section('title', 'Crear Producto - Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/productos.css') }}">

<div class="formulario-seccion">
    <h1>Crear Producto</h1>

    <form action="{{ route('producto.store') }}" method="POST" enctype="multipart/form-data">
        @csrf

        <label>Nombre</label>
        <input type="text" name="nombre_producto" value="{{ old('nombre_producto') }}" required>

     <br><br>
        <label>Descripción</label>
        <textarea name="descripcion">{{ old('descripcion') }}</textarea>
       <br><br>

        <label>Valor</label>
        <input type="number" name="valor" value="{{ old('valor') }}" required>
       <br><br>

        <label>Categoría</label>
        <select name="categoria" required>
            <option value="">-- Seleccione --</option>
            @foreach(['Hamburguesas','Perros','Empanadas','Bebidas','Guarniciones','Especias y Condimentos','Salsas y Aderezos','Otros'] as $cat)
                <option value="{{ $cat }}" @selected(old('categoria') == $cat)>{{ $cat }}</option>
            @endforeach
        </select>
        <br><br>
        <label>Imagen</label>
        <input type="file" name="imagen">

        <h3>Materias Primas</h3>
        <div id="materias-container">
            <div class="materia-item">
                <select name="materias_primas[0][id]" required>
                    <option value="">-- Seleccione --</option>
                    @foreach($materiasPrimas as $mp)
                        <option value="{{ $mp->id }}">{{ $mp->nombre_materia_prima }}</option>
                    @endforeach
                </select>
                <input type="number" name="materias_primas[0][cantidad_usada]" placeholder="Cantidad usada" required>
            </div>
        </div>
        <button type="button" id="add-materia" class="btn btn-secundario">+ Agregar Materia Prima</button>

        <div class="form-actions">
            <button type="submit" class="btn btn-crear">Guardar</button>
            <a href="{{ route('producto.index') }}" class="btn btn-cancelar">Cancelar</a>
        </div>
    </form>
</div>

<script>
    let index = 1;
    document.getElementById('add-materia').addEventListener('click', function() {
        let container = document.getElementById('materias-container');
        let div = document.createElement('div');
        div.classList.add('materia-item');
        div.innerHTML = `
            <select name="materias_primas[${index}][id]" required>
                <option value="">-- Seleccione --</option>
                @foreach($materiasPrimas as $mp)
                    <option value="{{ $mp->id }}">{{ $mp->nombre_materia_prima }}</option>
                @endforeach
            </select>
            <input type="number" name="materias_primas[${index}][cantidad_usada]" placeholder="Cantidad usada" required>
        `;
        container.appendChild(div);
        index++;
    });
</script>
@endsection
