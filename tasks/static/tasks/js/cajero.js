
function insertarNumero(numero) {
      const input = document.getElementById("codigoManual");
      input.value += numero;
      calcularCambio();
    }

    function borrarUltimoCaracter() {
      const input = document.getElementById("codigoManual");
      input.value = input.value.slice(0, -1);
    }

    function calcularCambio() {
      const total = parseFloat(document.getElementById('total').innerText.replace('$', ''));
      const efectivo = parseFloat(document.getElementById('efectivo').value || 0);
      const cambio = efectivo - total;
      document.getElementById('cambio').innerText = `$${cambio.toFixed(2)}`;
    }

    function buscarProductoManual() {
      const codigo = document.getElementById('codigoManual').value;
      if (!codigo) {
        alert('Por favor ingrese un código de barras');
        return;
      }

      // Lógica para buscar el producto por el código
      alert('Buscando producto con código: ' + codigo);
    }

    function abrirEscaner() {
      document.getElementById('modalEscaner').style.display = 'flex';
      iniciarEscaner();
    }

    function cerrarEscaner() {
      document.getElementById('modalEscaner').style.display = 'none';
      detenerEscaner();
    }

    function iniciarEscaner() {
      // Código para iniciar el escáner con Quagga
      Quagga.init({
        inputStream: {
          name: 'Live',
          type: 'LiveStream',
          constraints: {
            facingMode: 'environment'
          }
        },
        decoder: {
          readers: ['ean_reader', 'ean_8_reader', 'code_128_reader']
        }
      }, function(err) {
        if (err) {
          console.log(err);
          return;
        }
        Quagga.start();
      });

      Quagga.onDetected(function(data) {
        console.log(data);
        const codigo = data.codeResult.code;
        document.getElementById('codigoManual').value = codigo;
      });
    }

    function detenerEscaner() {
      Quagga.stop();
    }

    function toggleNumpad() {
        document.getElementById("numpad-panel").style.display = "flex";
      }
      
      function addDigit(digit) {
        const passInput = document.getElementById("efectivo");
        passInput.value += digit;
      }
      
      function backspace() {
        const passInput = document.getElementById("efectivo");
        passInput.value = passInput.value.slice(0, -1);
      }
      
      function togglePassword() {
        const passInput = document.getElementById("efectivo");
        passInput.type = passInput.type === "password" ? "text" : "password";
      }
      
      document.addEventListener("DOMContentLoaded", function () {
        const form = document.querySelector("form");
        const loading = document.getElementById("loading");
        if (form && loading) {
          form.addEventListener("submit", () => {
            loading.style.display = "block";
          });
        }
      });