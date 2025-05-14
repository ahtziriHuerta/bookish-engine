function toggleNumpad() {
    document.getElementById("logo-img").style.display = "none";
    document.getElementById("numpad-panel").style.display = "flex";
  }
  
  function addDigit(digit) {
    const passInput = document.getElementById("password");
    passInput.value += digit;
  }
  
  function backspace() {
    const passInput = document.getElementById("password");
    passInput.value = passInput.value.slice(0, -1);
  }
  
  function clearPassword() {
    document.getElementById("password").value = '';
  }
  
  function togglePassword() {
    const passInput = document.getElementById("password");
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
  