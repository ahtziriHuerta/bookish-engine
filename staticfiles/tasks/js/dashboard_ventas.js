document.addEventListener("DOMContentLoaded", () => {
  // 🔹 Gráfico de Métodos de Pago
  try {
    const rawData = JSON.parse(document.getElementById("metodos_pago").textContent);

    const labels = rawData.map(item => item.metodo_pago);
    const valores = rawData.map(item => parseFloat(item.total)); // 💡 Asegura que sean números

    const ctx = document.getElementById("graficoMetodoPago").getContext("2d");

    new Chart(ctx, {
      type: "pie",
      data: {
        labels: labels,
        datasets: [{
          label: "Ingresos por Método de Pago",
          data: valores,
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const value = context.raw;
                return `$${parseFloat(value).toFixed(2)}`;
              }
            }
          },
          title: {
            display: true,
            text: "Métodos de Pago"
          }
        }
      }
    });
  } catch (error) {
    console.error("❌ Error al parsear los datos para el gráfico:", error);
  }

  // 🔹 Buscador en la tabla de ventas
  const buscador = document.getElementById("buscadorVentas");
  if (buscador) {
    buscador.addEventListener("input", () => {
      const filtro = buscador.value.toLowerCase();
      const filas = document.querySelectorAll("tbody tr");

      filas.forEach(fila => {
        const texto = fila.textContent.toLowerCase();
        fila.style.display = texto.includes(filtro) ? "" : "none";
      });
    });
  }
});
