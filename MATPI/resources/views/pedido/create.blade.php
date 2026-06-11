@extends($layout)

@section('title', 'Crear Pedido - Matpi')

@section('content')
<link rel="stylesheet" href="{{ asset('css/pedidos.css') }}">

<div class="formulario-seccion">
    <h1>Crear Pedido</h1>

    @if(session('success'))
        <div class="alert alert-success">{{ session('success') }}</div>
    @endif

    <form action="{{ route('pedido.store') }}" method="POST">
        @csrf

        <label>Mesa</label>
        <input type="number" name="mesa" value="{{ old('mesa') }}" min="1">
        <br><br>

        <label>Número de Personas</label>
        <input type="number" name="numero_personas" value="{{ old('numero_personas') }}" min="1">
        <br><br>

        <label>ID Cliente</label>
        <input type="text" name="ID_Cliente" value="{{ old('ID_Cliente') }}" placeholder="Escriba el ID del cliente">
        <br><br>

        <h3>Productos</h3>
        <div id="productos-container">
            <div class="producto-item">
                <select name="productos[0][id]" class="producto-select" required>
                    <option value="">-- Seleccione --</option>
                    @foreach($productos as $producto)
                        <option value="{{ $producto->id }}" data-precio="{{ $producto->Precio }}">
                            {{ $producto->nombre_producto }} - ${{ $producto->Precio }}
                        </option>
                    @endforeach
                </select>
                <input type="number" name="productos[0][cantidad]" value="1" min="1" class="cantidad-input" required>
                <button type="button" class="btn btn-eliminar">Eliminar</button>
            </div>
        </div>

        <button type="button" id="add-producto" class="btn btn-secundario">+ Agregar Producto</button>

        <h3>Total: $<span id="total">0</span></h3>

        <div class="form-actions">
            <button type="submit" class="btn btn-crear">Guardar Pedido</button>
            <a href="{{ route('pedido.index') }}" class="btn btn-cancelar">Cancelar</a>
        </div>
    </form>
</div>

<script>
let index = 1;
const productosContainer = document.getElementById('productos-container');
const addBtn = document.getElementById('add-producto');
const totalSpan = document.getElementById('total');

// Función para calcular total
function calcularTotal() {
    let total = 0;
    productosContainer.querySelectorAll('.producto-item').forEach(item => {
        const select = item.querySelector('.producto-select');
        const cantidad = parseInt(item.querySelector('.cantidad-input').value) || 0;
        const precio = parseInt(select.selectedOptions[0]?.dataset.precio) || 0;
        total += cantidad * precio;
    });
    totalSpan.textContent = total;
}

// Agregar producto
addBtn.addEventListener('click', () => {
    const div = document.createElement('div');
    div.classList.add('producto-item');
    div.innerHTML = `
        <select name="productos[${index}][id]" class="producto-select" required>
            <option value="">-- Seleccione --</option>
            @foreach($productos as $producto)
                <option value="{{ $producto->id }}" data-precio="{{ $producto->Precio }}">
                    {{ $producto->nombre_producto }} - ${{ $producto->Precio }}
                </option>
            @endforeach
        </select>
        <input type="number" name="productos[${index}][cantidad]" value="1" min="1" class="cantidad-input" required>
        <button type="button" class="btn btn-eliminar">Eliminar</button>
    `;
    productosContainer.appendChild(div);
    index++;
    actualizarEventos();
    calcularTotal();
});

// Actualizar eventos de inputs y botones eliminar
function actualizarEventos() {
    productosContainer.querySelectorAll('.cantidad-input, .producto-select').forEach(input => {
        input.addEventListener('input', calcularTotal);
    });

    productosContainer.querySelectorAll('.btn-eliminar').forEach(btn => {
        btn.onclick = () => {
            btn.parentElement.remove();
            calcularTotal();
        };
    });
}

// Inicializar eventos para el primer producto
actualizarEventos();
calcularTotal();
</script>
@endsection
