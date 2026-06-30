const formatter = new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0
});

function sincronizarClienteId(valor) {
    const datalist = document.getElementById('clientes_list');
    const hiddenInput = document.getElementById('txt_cliente_id');
    const opciones = datalist.options;
    let clienteId = null;

    for (let i = 0; i < opciones.length; i++) {
        if (opciones[i].value === valor) {
            clienteId = opciones[i].dataset.id;
            break;
        }
    }

    hiddenInput.value = clienteId || "";
    
    // Si la función de filtrado existe (por ejemplo, en el select de reservas)
    if (typeof filtrarReservas === "function") {
        filtrarReservas(clienteId);
    }
}

function filtrarReservas(clienteId) {
    const selectReserva = document.getElementById('txt_reserva');
    if (!selectReserva) return;
    const opciones = selectReserva.options;
    let encontradas = 0;

    // Guardar el valor seleccionado antes de filtrar
    const valorOriginal = selectReserva.value;

    if (!clienteId) {
        selectReserva.value = "";
        selectReserva.disabled = true;
        for (let i = 1; i < opciones.length; i++) {
            opciones[i].style.display = 'none';
        }
        const helpText = document.getElementById('reserva-help');
        if (helpText) helpText.innerText = "Selecciona un cliente para ver sus reservas.";
        return;
    }

    for (let i = 1; i < opciones.length; i++) {
        const idC = opciones[i].dataset.cliente;
        if (idC === clienteId) {
            opciones[i].style.display = 'block';
            encontradas++;
        } else {
            opciones[i].style.display = 'none';
        }
    }

    if (encontradas > 0) {
        selectReserva.disabled = false;
        // Restaurar el valor original si pertenece al cliente seleccionado, si no, vaciar
        let opcionSeleccionada = null;
        for (let i = 0; i < opciones.length; i++) {
            if (opciones[i].value === valorOriginal) {
                opcionSeleccionada = opciones[i];
                break;
            }
        }
        if (opcionSeleccionada && (opcionSeleccionada.dataset.cliente === clienteId || valorOriginal === "")) {
            selectReserva.value = valorOriginal;
        } else {
            selectReserva.value = "";
        }
        const helpText = document.getElementById('reserva-help');
        if (helpText) helpText.innerText = `Se encontraron ${encontradas} reserva(s) para este cliente.`;
    } else {
        selectReserva.value = "";
        selectReserva.disabled = true;
        const helpText = document.getElementById('reserva-help');
        if (helpText) helpText.innerText = "Este cliente no tiene reservas activas.";
    }
}

function eliminarFilaProducto(boton) {
    const tbody = document.getElementById('body-productos');
    if (tbody.rows.length > 1) {
        boton.closest('tr').remove();
        calcularTotal();
    } else {
        alert("El pedido debe tener al menos un item.");
    }
}

function toggleDetalles(boton) {
    const div = boton.nextElementSibling;
    div.style.display = (div.style.display === "none") ? "block" : "none";
    boton.innerText = (div.style.display === "none") ? "⚙️ Personalizar" : "🔼 Cerrar";
}

function actualizarComposicion_y_Precio(elemento, excluidasPreseleccionadas = []) {
    const fila = elemento.closest('tr');
    const selectElement = fila.querySelector('.select-producto');
    const opcion = selectElement.options[selectElement.selectedIndex];
    const listaExcl = fila.querySelector('.lista-exclusiones');
    const indice = fila.getAttribute('data-indice') || fila.dataset.indice || 0;
    const selectCant = fila.querySelector('.select-cantidad');

    if (opcion.value && listaExcl) {
        const composicion = JSON.parse(opcion.dataset.composicion || "[]");

        // 1. Construir HTML solo si el cambio NO vino de un checkbox
        if (elemento.type !== 'checkbox') {
            let html = "";
            composicion.forEach(mp => {
                if (mp.es_prioridad) return; // Si es prioridad, no se puede excluir del pedido
                const isExpired = mp.expired || false;
                const isBad = mp.stock <= 0 || isExpired;
                const labelStyle = isBad ? 'style="border-color: #ef4444; background: #fef2f2;"' : '';
                const spanStyle = isBad ? 'style="color: #b91c1c; font-weight: bold;"' : '';
                let statusText = '';
                if (isExpired) {
                    statusText = '(¡VENCIDO!)';
                } else if (mp.stock <= 0) {
                    statusText = '(¡AGOTADO!)';
                }

                const checked = (excluidasPreseleccionadas.includes(mp.id) || isExpired) ? 'checked' : '';
                const disabled = isExpired ? 'disabled' : '';

                html += `
                    <label class="exclusion-item" ${labelStyle}>
                        <input type="checkbox" name="producto_exclusiones_${indice}[]" value="${mp.id}" onchange="actualizarComposicion_y_Precio(this)" ${checked} ${disabled}>
                        <span ${spanStyle}>
                            Sin ${mp.nombre} ${statusText}
                        </span>
                    </label>
                `;
            });
            listaExcl.innerHTML = html || "<p style='font-size: 0.8rem; color: #94a3b8;'>Sin ingredientes modificables.</p>";
        }

        // 2. Calcular los límites de stock
        let stockLimitado = Infinity;
        let agotado = false;
        const checkedIds = new Set(Array.from(fila.querySelectorAll(`.lista-exclusiones input[type="checkbox"]:checked`)).map(cb => Number.parseInt(cb.value, 10)));

        composicion.forEach(mp => {
            if (!checkedIds.has(mp.id)) {
                const posible = Math.floor(mp.stock / mp.cantidad_usada);
                if (posible < stockLimitado) stockLimitado = posible;
                if (mp.stock <= 0) agotado = true;
            }
        });

        // 3. Aplicar estado visual si faltan ingredientes vitales
        if (agotado) {
            fila.style.border = "2px solid #ef4444";
            fila.style.backgroundColor = "#fff5f5";
        } else {
            fila.style.border = "";
            fila.style.backgroundColor = "";
        }

        if (stockLimitado <= 10 && stockLimitado > 0) {
            Array.from(selectCant.options).forEach(opt => {
                if (Number.parseInt(opt.value, 10) > stockLimitado) {
                    opt.disabled = true;
                    opt.style.color = "#ccc";
                } else {
                    opt.disabled = false;
                    opt.style.color = "inherit";
                }
            });

            if (Number.parseInt(selectCant.value, 10) > stockLimitado) {
                selectCant.value = stockLimitado;
            }
        } else {
            Array.from(selectCant.options).forEach(opt => {
                opt.disabled = false;
                opt.style.color = "inherit";
            });
        }
    } else if (listaExcl) {
        listaExcl.innerHTML = "";
        fila.style.border = "";
        fila.style.backgroundColor = "";
    }

    calcularTotal();
}

function calcularTotal() {
    let totalGeneral = 0;
    let totalItems = 0;
    const filas = document.querySelectorAll('.fila-producto');

    filas.forEach(fila => {
        const select = fila.querySelector('.select-producto');
        const selectCant = fila.querySelector('.select-cantidad');
        const subtotalFila = fila.querySelector('.subtotal-fila');

        const seleccionada = select.options[select.selectedIndex];
        if (seleccionada && seleccionada.value) {
            const precio = Number.parseFloat(seleccionada.dataset.precio || 0);
            const cantidad = Number.parseInt(selectCant.value || 0, 10);
            const totalFila = precio * cantidad;

            subtotalFila.innerText = formatter.format(totalFila);
            totalGeneral += totalFila;
            totalItems += cantidad;
        } else {
            subtotalFila.innerText = "$0";
        }
    });

    const displayTotal = document.getElementById('valor-total-display');
    if (displayTotal) displayTotal.innerText = formatter.format(totalGeneral);
    
    const inputValor = document.getElementById('txt_valor');
    if (inputValor) inputValor.value = totalGeneral;
    
    const spanTotalItems = document.getElementById('span-total-items');
    if (spanTotalItems) spanTotalItems.innerText = totalItems;
}

function validarStockYSubmit(e, accionTexto, esEdicion = false) {
    const clienteId = document.getElementById('txt_cliente_id').value;
    const clienteNombre = document.getElementById('txt_cliente_search').value;

    if (clienteNombre && !clienteId) {
        alert("No se puede " + accionTexto + " el pedido: El cliente '" + clienteNombre + "' no existe. Selecciónelo de la lista o regístrelo primero.");
        e.preventDefault();
        return false;
    }

    if (esEdicion) {
        return true;
    }

    const filas = document.querySelectorAll('.fila-producto');
    let error = false;
    let msg = "";

    filas.forEach(fila => {
        const select = fila.querySelector('.select-producto');
        const opcion = select.options[select.selectedIndex];
        if (!opcion || !opcion.value) return;

        const composicion = JSON.parse(opcion.dataset.composicion || "[]");
        const cantidad = Number.parseInt(fila.querySelector('.select-cantidad').value, 10);
        const excluidas = new Set(Array.from(fila.querySelectorAll(`.lista-exclusiones input[type="checkbox"]:checked`)).map(cb => Number.parseInt(cb.value, 10)));

        composicion.forEach(mp => {
            if (!excluidas.has(mp.id)) {
                if (mp.stock < (mp.cantidad_usada * cantidad)) {
                    error = true;
                    msg += `- ${opcion.text.trim()}: Insumo "${mp.nombre}" insuficiente (Disponible: ${mp.stock})\n`;
                }
            }
        });
    });

    if (error) {
        alert("No se puede " + accionTexto + " el pedido por falta de stock:\n\n" + msg);
        e.preventDefault();
        return false;
    }
    
    return true;
}

// Inicializar eventos comunes
document.addEventListener('DOMContentLoaded', () => {
    const bodyProductos = document.getElementById('body-productos');
    if (bodyProductos) {
        bodyProductos.addEventListener('change', function(e) {
            if (e.target.classList.contains('select-producto') || e.target.classList.contains('select-cantidad')) {
                calcularTotal();
            }
        });
    }
});
