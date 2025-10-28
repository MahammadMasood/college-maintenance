
//script for new request page  
document.addEventListener('DOMContentLoaded', function () {
  const selectedItemsInput = document.getElementById('selectedItems');
  const totalAmountInput = document.getElementById('totalAmount');
  const grandTotalEl = document.getElementById('grandTotal');
  const rows = document.querySelectorAll('#equipmentTable tbody tr');

  function calculateTotals() {
    let total = 0;
    let selected = [];

    rows.forEach(row => {
      const checkbox = row.querySelector('.item-checkbox');
      const qtyInput = row.querySelector('.qty-input');
      const price = parseFloat(row.querySelector('.price').innerText) || 0;
      const subtotalCell = row.querySelector('.subtotal');
      const qty = parseInt(qtyInput.value) || 0;
      let subtotal = 0;

      if (checkbox.checked && qty > 0) {
        subtotal = price * qty;
        subtotalCell.innerText = subtotal.toFixed(2);
        total += subtotal;

        selected.push({
          device: row.querySelector('.device').innerText.trim(),
          brand: row.querySelector('.brand').innerText.trim(),
          size: row.querySelector('.size').innerText.trim(),
          price: price,
          usage: row.querySelector('.usage').innerText.trim(),
          remarks: row.querySelector('.remarks').innerText.trim(),
          quantity: qty,
          subtotal: subtotal
        });
      } else {
        subtotalCell.innerText = "0";
      }
    });

    grandTotalEl.innerText = total.toFixed(2);
    if (selectedItemsInput) selectedItemsInput.value = JSON.stringify(selected);
    if (totalAmountInput) totalAmountInput.value = total.toFixed(2);
  }

  // Attach listeners
  rows.forEach(row => {
    const checkbox = row.querySelector('.item-checkbox');
    const qtyInput = row.querySelector('.qty-input');
    checkbox.addEventListener('change', calculateTotals);
    qtyInput.addEventListener('input', calculateTotals);
  });

  // Prefill if editing (existingItems comes from template)
  try {
    if (typeof existingItems !== 'undefined' && Array.isArray(existingItems) && existingItems.length) {
      existingItems.forEach(item => {
        rows.forEach(row => {
          const device = row.querySelector('.device').innerText.trim();
          const size = row.querySelector('.size').innerText.trim();
          const brand = row.querySelector('.brand').innerText.trim();

          // ✅ Match by device + size + brand/model to avoid false matches
          if (device === item.device && size === item.size && brand === item.brand) {
            const checkbox = row.querySelector('.item-checkbox');
            const qtyInput = row.querySelector('.qty-input');
            checkbox.checked = true;
            qtyInput.value = item.quantity || 1;
          }
        });
      });
    }
  } catch (err) {
    console.error("Prefill error:", err);
  }

  // Initial calculation
  calculateTotals();
});



document.addEventListener("DOMContentLoaded", () => {

  /* ===============================
     1️⃣ STATUS CARD FILTER HANDLING
     =============================== */
  const statusCards = document.querySelectorAll(".card");

  statusCards.forEach((card) => {
    card.addEventListener("click", () => {
      const title = card.querySelector("h3").textContent.trim();

      let status = "";
      if (title.includes("Pending")) status = "Pending";
      else if (title.includes("Approved")) status = "Approved";
      else if (title.includes("Rejected")) status = "Rejected";

      if (status) {
        // Redirect with status query
        window.location.href = `?status=${status}`;
      } else {
        // Reset filter
        window.location.href = window.location.pathname;
      }
    });
  });

  /* ===============================
     2️⃣ DEPARTMENT DROPDOWN HANDLING
     =============================== */
  const deptLink = document.getElementById("deptLink");

  if (deptLink) {
    const deptDropdown = document.getElementById("deptDropdown");

    if (deptDropdown) {
      // Toggle dropdown visibility
      deptLink.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        const isVisible = deptDropdown.style.display === "flex";
        deptDropdown.style.display = isVisible ? "none" : "flex";
      });

      // Close dropdown when clicking outside
      document.addEventListener("click", (e) => {
        if (!deptLink.contains(e.target) && !deptDropdown.contains(e.target)) {
          deptDropdown.style.display = "none";
        }
      });
    }
  }

});


