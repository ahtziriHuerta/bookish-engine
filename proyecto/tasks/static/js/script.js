const ticketList = document.getElementById('ticket-list');
const totalDisplay = document.getElementById('total');
const taxDisplay = document.getElementById('tax');
const discountDisplay = document.getElementById('discount');
let ticket = [];

document.querySelectorAll('.product').forEach(item => {
  item.addEventListener('click', () => {
    const name = item.dataset.name;
    const price = parseFloat(item.dataset.price);
    addToTicket({ name, price });
  });
});

function addToTicket(product) {
  const existing = ticket.find(item => item.name === product.name);
  if (existing) {
    existing.qty += 1;
  } else {
    ticket.push({ ...product, qty: 1 });
  }
  updateTicket();
}

function updateTicket() {
  ticketList.innerHTML = '';
  let subtotal = 0;
  ticket.forEach(item => {
    const li = document.createElement('li');
    li.innerHTML = `${item.name} x ${item.qty} <span>$${(item.qty * item.price).toFixed(2)}</span>`;
    ticketList.appendChild(li);
    subtotal += item.qty * item.price;
  });

  const discount = subtotal > 20 ? 2.00 : 0.00;
  const tax = subtotal * 0.16;
  const total = subtotal - discount + tax;

  discountDisplay.textContent = `$${discount.toFixed(2)}`;
  taxDisplay.textContent = `$${tax.toFixed(2)}`;
  totalDisplay.textContent = `$${total.toFixed(2)}`;
}
