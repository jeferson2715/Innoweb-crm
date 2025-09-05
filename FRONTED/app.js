document.addEventListener('DOMContentLoaded', () => {
  // Mostrar alerta pendiente guardada antes de un redirect
  const pending = sessionStorage.getItem('swal');
  if (pending) {
    sessionStorage.removeItem('swal');
    try { Swal.fire(JSON.parse(pending)); } catch {}
  }

  const form          = document.getElementById('personaFormulario');
  const btnIrDatos    = document.getElementById('btnIrDatos');
  const btnAgregar    = document.getElementById('btnAgregar');
  const btnActualizar = document.getElementById('btnActualizar');
  const tbody         = document.getElementById('datosPersonaBD');

  // Ir a /datos
  if (btnIrDatos) {
    btnIrDatos.addEventListener('click', () => { window.location.href = '/datos'; });
  }

  // =============== FORMULARIO (Innoweb.html) ===============
  if (form) {
    const params    = new URLSearchParams(window.location.search);
    const editingId = params.get('id');

    if (editingId) {
      if (btnAgregar)    btnAgregar.style.display = 'none';
      if (btnActualizar) btnActualizar.style.display = 'inline-block';
      precargarPersona(editingId);
    }

    // CREAR (POST)
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (editingId) return;

      const payload = { persona: recogerFormulario(true) };
      try {
        const res  = await fetch('/agregarPersonaBD', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (res.ok && data.ok) {
          // Guardamos la alerta para mostrarla al llegar a /datos
          sessionStorage.setItem('swal', JSON.stringify({
            icon: 'success',
            title: 'Cliente agregado con éxito',
            timer: 1600,
            showConfirmButton: false
          }));
          window.location.href = '/datos';
        } else {
          Swal.fire({
            icon: 'error',
            title: 'No se pudo guardar',
            text: (data?.errores && data.errores.join('\n')) || data?.mensaje || 'Error al agregar el cliente'
          });
        }
      } catch {
        Swal.fire({ icon: 'error', title: 'Error de red', text: 'No se pudo guardar.' });
      }
    });

    // ACTUALIZAR (PUT)
    if (btnActualizar) {
      btnActualizar.addEventListener('click', async () => {
        if (!editingId) return;

        const datos = recogerFormulario(false);
        try {
          const res  = await fetch(`/actualizarPersona/${encodeURIComponent(editingId)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
          });
          const data = await res.json();

          if (res.ok && data.ok) {
            sessionStorage.setItem('swal', JSON.stringify({
              icon: 'success',
              title: 'Cliente actualizado con éxito',
              timer: 1600,
              showConfirmButton: false
            }));
            window.location.href = '/datos';
          } else {
            const msg = (data?.errores && data.errores.join('\n')) || data?.mensaje || 'Error al actualizar el cliente';
            Swal.fire({ icon: 'error', title: 'Error al actualizar', text: msg });
          }
        } catch {
          Swal.fire({ icon: 'error', title: 'Error de red', text: 'No se pudo actualizar.' });
        }
      });
    }
  }

  // =============== TABLA (datos.html) ===============
  if (tbody) {
    cargarTabla();

    async function cargarTabla() {
      try {
        const res      = await fetch('/datosDeLaBase');
        const personas = await res.json();

        tbody.innerHTML = personas.map(p => `
          <tr>
            <td>${p.id ?? ''}</td>
            <td>${p.fecha_registro ?? ''}</td>
            <td>${p.estado ?? ''}</td>
            <td>${p.empresa ?? ''}</td>
            <td>${p.nombre ?? ''}</td>
            <td>${p.email ?? ''}</td>
            <td>${p.telefono ?? ''}</td>
            <td>${p.ciudad_pais ?? ''}</td>
            <td>${p.tipo_proyecto ?? ''}</td>
            <td>${p.estado_proyecto ?? ''}</td>
            <td>${p.responsable ?? ''}</td>
            <td>
              <button class="btn btn-actualizar" data-id="${p.id}">Editar</button>
              <button class="btn btn-eliminar"  data-id="${p.id}">Eliminar</button>
            </td>
          </tr>
        `).join('');

        // EDITAR
        document.querySelectorAll('.btn-actualizar').forEach(b => {
          b.addEventListener('click', () => {
            const id = b.dataset.id;
            window.location.href = `/?id=${encodeURIComponent(id)}`;
          });
        });

        // ELIMINAR (confirmación + resultado)
        document.querySelectorAll('.btn-eliminar').forEach(b => {
          b.addEventListener('click', async () => {
            const id = b.dataset.id;

            const confirm = await Swal.fire({
              title: '¿Eliminar cliente?',
              text: `Se eliminará el cliente ${id}. Esta acción no se puede deshacer.`,
              icon: 'warning',
              showCancelButton: true,
              confirmButtonText: 'Sí, eliminar',
              cancelButtonText: 'Cancelar',
              reverseButtons: true
            });
            if (!confirm.isConfirmed) return;

            try {
              const del = await fetch(`/eliminarPersona/${encodeURIComponent(id)}`, { method: 'DELETE' });
              if (del.ok) {
                await Swal.fire({ icon: 'success', title: 'Cliente eliminado', timer: 1300, showConfirmButton: false });
                cargarTabla();
              } else {
                const txt = await del.text();
                Swal.fire({ icon: 'error', title: 'No se pudo eliminar', text: txt || 'Inténtalo de nuevo.' });
              }
            } catch {
              Swal.fire({ icon: 'error', title: 'Error de red', text: 'No se pudo contactar al servidor.' });
            }
          });
        });

      } catch {
        tbody.innerHTML = `<tr><td colspan="12">Error al cargar datos.</td></tr>`;
      }
    }
  }

  // =============== Helpers ===============
  function recogerFormulario(incluirId) {
    const data = {
      estado:          document.getElementById('estado').value,
      empresa:         document.getElementById('empresa').value,
      nombre:          document.getElementById('nombre').value,
      email:           document.getElementById('email').value,
      telefono:        document.getElementById('telefono').value,
      ciudad_pais:     document.getElementById('ciudad_pais').value,
      tipo_proyecto:   document.getElementById('tipo_proyecto').value,
      estado_proyecto: document.getElementById('estado_proyecto').value,
      responsable:     document.getElementById('responsable').value
    };
    if (incluirId) data.id = Number(document.getElementById('id').value);
    return data;
  }

  async function precargarPersona(id) {
    try {
      const res  = await fetch(`/buscarPersona/${encodeURIComponent(id)}`);
      const data = await res.json();
      const p    = Array.isArray(data) ? data[0] : data;
      if (!p) return;

      document.getElementById('id').value              = p.id ?? '';
      document.getElementById('estado').value          = p.estado ?? 'Nuevo';
      document.getElementById('empresa').value         = p.empresa ?? '';
      document.getElementById('nombre').value          = p.nombre ?? '';
      document.getElementById('email').value           = p.email ?? '';
      document.getElementById('telefono').value        = p.telefono ?? '';
      document.getElementById('ciudad_pais').value     = p.ciudad_pais ?? '';
      document.getElementById('tipo_proyecto').value   = p.tipo_proyecto ?? 'Pagina web';
      document.getElementById('estado_proyecto').value = p.estado_proyecto ?? 'Pendiente';
      document.getElementById('responsable').value     = p.responsable ?? '';

      document.getElementById('id').readOnly = true; // opcional
    } catch {
      Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudieron cargar los datos para editar.' });
    }
  }
});
