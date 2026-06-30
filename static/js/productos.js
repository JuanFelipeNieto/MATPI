function agregarFila() {
    const tbody = document.getElementById('body-composicion');
    const filas = tbody.getElementsByClassName('fila-materia');
    const nuevaFila = filas[0].cloneNode(true);
    const index = filas.length + 1;

    const select = nuevaFila.querySelector('.select-materia');
    const labelSelect = nuevaFila.querySelector('.label-select');
    if(select) {
        select.value = "";
        select.id = `select_materia_${index}`;
    }
    if(labelSelect) {
        labelSelect.setAttribute('for', `select_materia_${index}`);
    }

    const inputEquiv = nuevaFila.querySelector('.input-equiv');
    const labelInput = nuevaFila.querySelector('.label-input');
    if(inputEquiv) {
        inputEquiv.value = "";
        inputEquiv.id = `materia_cantidad_${index}`;
    }
    if(labelInput) {
        labelInput.setAttribute('for', `materia_cantidad_${index}`);
    }

    const inputUnidadOculto = nuevaFila.querySelector('.input-unidad-texto');
    const labelUnidad = nuevaFila.querySelector('.label-unidad');
    if(inputUnidadOculto) {
        inputUnidadOculto.value = "";
        inputUnidadOculto.id = `materia_unidad_${index}`;
    }
    if(labelUnidad) {
        labelUnidad.setAttribute('for', `materia_unidad_${index}`);
    }

    const unitLabels = nuevaFila.querySelectorAll('.unit-label');
    const msgUnidades = nuevaFila.querySelector('.msg-unidades');

    if(inputUnidadOculto) inputUnidadOculto.value = "";
    if(unitLabels) unitLabels.forEach(l => l.textContent = "");
    if(msgUnidades) msgUnidades.textContent = "";

    const hiddenPrio = nuevaFila.querySelector('.input-prioridad-valor');
    const checkboxPrio = nuevaFila.querySelector('.checkbox-prioridad');
    if (hiddenPrio) hiddenPrio.value = "0";
    if (checkboxPrio) checkboxPrio.checked = false;

    tbody.appendChild(nuevaFila);
}

function eliminarFila(boton) {
    const tbody = document.getElementById('body-composicion');
    if (tbody.rows.length > 1) {
        boton.closest('tr').remove();
    } else {
        alert("La comida debe tener al menos un ingrediente.");
    }
}

function actualizarEquivalencia(selectObj) {
    const tr = selectObj.closest('tr');
    const opcion = selectObj.options[selectObj.selectedIndex];

    const equiv = Number.parseFloat(opcion.dataset.equiv) || 0;
    const unidad = opcion.dataset.unidad || '';

    const inputCantidad = tr.querySelector('.input-equiv');
    const inputUnidadOculto = tr.querySelector('.input-unidad-texto');
    const labelsUnidad = tr.querySelectorAll('.unit-label');

    if (equiv > 0) {
        inputCantidad.value = equiv;
        inputUnidadOculto.value = unidad;
        labelsUnidad.forEach(label => label.textContent = unidad);
        actualizarUnidades(inputCantidad);
    } else {
        inputCantidad.value = "";
        inputUnidadOculto.value = "";
        labelsUnidad.forEach(label => label.textContent = "");
        tr.querySelector('.msg-unidades').textContent = "";
    }
}

function actualizarUnidades(inputObj) {
    const tr = inputObj.closest('tr');
    const select = tr.querySelector('.select-materia');
    const opcion = select.options[select.selectedIndex];
    if (!opcion || !opcion.value) return;

    const equivBase = Number.parseFloat(opcion.dataset.equiv) || 1;
    const cantidadActual = Number.parseFloat(inputObj.value) || 0;
    const numUnidades = (cantidadActual / equivBase).toFixed(2);
    const floatUnidades = Number.parseFloat(numUnidades);

    const msg = tr.querySelector('.msg-unidades');
    if (equivBase > 0 && cantidadActual > 0) {
        if (floatUnidades > 1) {
            msg.textContent = "⚠ Equivale a: " + floatUnidades + " unidad(es)";
            msg.style.color = "#e67e22"; // Naranja fuerte
            msg.classList.remove('text-success');
        } else {
            msg.textContent = "✔ Equivale a: " + floatUnidades + " unidad(es)";
            msg.style.color = "";
            msg.classList.add('text-success');
        }
    } else {
        msg.textContent = "";
    }
}

function sumarUnidad(btn) {
    const tr = btn.closest('tr');
    const inputObj = tr.querySelector('.input-equiv');
    const select = tr.querySelector('.select-materia');
    const opcion = select.options[select.selectedIndex];
    const equivBase = Number.parseFloat(opcion.dataset.equiv) || 0;

    if (equivBase > 0) {
        let actual = Number.parseFloat(inputObj.value) || 0;
        inputObj.value = (actual + equivBase).toFixed(2);
        actualizarUnidades(inputObj);
    }
}

function restarUnidad(btn) {
    const tr = btn.closest('tr');
    const inputObj = tr.querySelector('.input-equiv');
    const select = tr.querySelector('.select-materia');
    const opcion = select.options[select.selectedIndex];
    const equivBase = Number.parseFloat(opcion.dataset.equiv) || 0;

    if (equivBase > 0) {
        let actual = Number.parseFloat(inputObj.value) || 0;
        let nuevo = actual - equivBase;
        if (nuevo < 1) { nuevo = 1; }
        inputObj.value = nuevo.toFixed(2);
        actualizarUnidades(inputObj);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const inputImagen = document.getElementById('txt_imagen');
    if (inputImagen) {
        inputImagen.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const validExtensions = ['png', 'jpg', 'jpeg'];
                const fileExtension = file.name.split('.').pop().toLowerCase();
                if (!validExtensions.includes(fileExtension)) {
                    alert('Solo se permiten imágenes en formato JPG o PNG.');
                    this.value = ''; // Limpiar la selección
                }
            }
        });
    }
});
