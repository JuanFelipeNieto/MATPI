@extends($layout)

@section('title', 'Editar Producto - Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/productos.css') }}">

<div class="formulario-seccion">
    <h1>Editar Producto</h1>

    <form action="{{ route('producto.update', $producto) }}" method="POST" enctype="multipart/form-data" class="formulario-producto">
        @csrf
        @method('PUT')

        <div class="form-group">
            <label for="nombre_producto">Nombre</label>
            <input type="text" id="nombre_producto" name="nombre_producto" 
                   value="{{ old('nombre_producto', $producto->nombre_producto) }}" required>
        </div>

        <div class="form-group">
            <label for="descripcion">Descripción</label>
            <textarea id="descripcion" name="descripcion" rows="3">{{ old('descripcion', $producto->descripcion) }}</textarea>
        </div>

        <div class="form-group">
            <label for="valor">Valor</label>
            <input type="number" id="valor" name="valor" 
                   value="{{ old('valor', $producto->valor) }}" required>
        </div>

        <div class="form-group">
            <label for="categoria">Categoría</label>
            <select id="categoria" name="categoria" required>
                <option value="">-- Seleccione --</option>
                @foreach(['Hamburguesas','Perros','Empanadas','Bebidas','Guarniciones','Especias y Condimentos','Salsas y Aderezos','Otros'] as $cat)
                    <option value="{{ $cat }}" @selected(old('categoria', $producto->categoria) == $cat)>{{ $cat }}</option>
                @endforeach
            </select>
        </div>

        <div class="form-group imagen-group">
            <label>Imagen</label>
            @if($producto->imagen)
                <div class="preview-img">
                    <img src="{{ asset('storage/' . $producto->imagen) }}" alt="Imagen del producto" class="producto-preview">
                </div>
            @endif
            <input type="file" name="imagen" class="input-file">
        </div>

        {{-- 📦 Cantidad --}}
        <div class="form-group">
            <label for="cantidad">Cantidad disponible</label>
            <input type="number" id="cantidad" name="cantidad" 
                   value="{{ $producto->cantidad }}" readonly>
        </div>

        <h3>Materias Primas</h3>
        <div id="materias-container">
            @foreach($producto->materiasPrimas as $index => $mp)
                <div class="materia-item">
                    <select name="materias_primas[{{ $index }}][id]" required>
                        <option value="">-- Seleccione --</option>
                        @foreach($materiasPrimas as $mat)
                            <option value="{{ $mat->id }}" @selected($mat->id == $mp->id)>{{ $mat->nombre_materia_prima }}</option>
                        @endforeach
                    </select>
                    <input type="number" name="materias_primas[{{ $index }}][cantidad_usada]" 
                           value="{{ $mp->pivot->cantidad_usada }}" 
                           placeholder="Cantidad usada" required>
                    <button type="button" class="btn-remove">X</button>
                </div>
            @endforeach
        </div>
        <button type="button" id="add-materia" class="btn btn-secundario">+ Agregar Materia Prima</button>

        <div class="form-actions">
            <button type="submit" class="btn btn-crear">Guardar</button>
            <a href="{{ route('producto.index') }}" class="btn btn-cancelar">Cancelar</a>
        </div>
    </form>
</div>

<script>
    let index = {{ $producto->materiasPrimas->count() }};

    document.getElementById('add-materia').addEventListener('click', function() {
        let container = document.getElementById('materias-container');
        let div = document.createElement('div');
        div.classList.add('materia-item');
        div.innerHTML = `
            <select name="materias_primas[${index}][id]" required>
                <option value="">-- Seleccione --</option>
                @foreach($materiasPrimas as $mat)
                    <option value="{{ $mat->id }}">{{ $mat->nombre_materia_prima }}</option>
                @endforeach
            </select>
            <input type="number" name="materias_primas[${index}][cantidad_usada]" placeholder="Cantidad usada" required>
            <button type="button" class="btn-remove">❌</button>
        `;
        container.appendChild(div);
        index++;
    });

    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-remove')) {
            e.target.parentElement.remove();
        }
    });
</script>
@endsection
