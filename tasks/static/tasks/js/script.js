


const inputCodigo = document.getElementById('codigo_barras');

inputCodigo.addEventListener('keydown', async function(e) {
  if (e.key === 'Enter') {
    e.preventDefault();
    const codigo = inputCodigo.value.trim();

    try {
      const response = await fetch(`/buscar_producto/${codigo}/`);
      if (response.ok) {
        const producto = await response.json();
        addToTicket({
          name: producto.nombre,
          price: parseFloat(producto.precio)
        });
        inputCodigo.value = '';
      } else {
        alert('Producto no encontrado');
        inputCodigo.value = '';
      }
    } catch (error) {
      console.error('Error al buscar producto:', error);
    }
  }
});
