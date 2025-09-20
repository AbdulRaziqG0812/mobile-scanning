// Toggle password visibility (works for both Login & Register)
document.querySelectorAll(".toggle-password").forEach(icon => {
  icon.addEventListener("click", function() {
    const targetId = this.getAttribute("data-target");
    const input = document.getElementById(targetId);

    if (input) {
      if (input.type === "password") {
        input.type = "text";
        this.classList.remove("fa-eye-slash");
        this.classList.add("fa-eye");
      } else {
        input.type = "password";
        this.classList.remove("fa-eye");
        this.classList.add("fa-eye-slash");
      }
    }
  });
});

// Pagination for tables

document.addEventListener("DOMContentLoaded", function () {
  const rowsPerPage = 10; // jitni rows per page dikhani hain
  const table = document.querySelector(".paginated-table");
  const pagination = document.getElementById("pagination");
  if (!table || !pagination) return;

  const tbody = table.querySelector("tbody");
  const rows = Array.from(tbody.querySelectorAll("tr"));
  if (rows.length === 0) return;

  let currentPage = 1;
  const totalPages = Math.ceil(rows.length / rowsPerPage);

  function displayPage(page) {
    currentPage = page;
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;

    rows.forEach((row, index) => {
      row.style.display = (index >= start && index < end) ? "" : "none";
    });

    updatePagination();
  }

  function updatePagination() {
    pagination.innerHTML = ""; // ✅ sirf ek hi block me sab buttons add hote rahenge

    const createButton = (content, disabled = false, active = false, onClick = null) => {
      const btn = document.createElement("button");
      btn.innerHTML = content;
      btn.disabled = disabled;
      if (active) btn.classList.add("active");
      if (!disabled && onClick) btn.addEventListener("click", onClick);
      return btn;
    };

    // Prev button
    pagination.appendChild(
      createButton("«", currentPage === 1, false, () => displayPage(currentPage - 1))
    );

    // All page numbers (ek hi block me)
    for (let i = 1; i <= totalPages; i++) {
      pagination.appendChild(
        createButton(i, false, i === currentPage, () => displayPage(i))
      );
    }

    // Next button
    pagination.appendChild(
      createButton("»", currentPage === totalPages, false, () => displayPage(currentPage + 1))
    );
  }

  displayPage(1);
});



 // Auto-hide flash messages after 3 seconds
    document.addEventListener("DOMContentLoaded", () => {
      const alerts = document.querySelectorAll('.alert');
      alerts.forEach(alert => setTimeout(() => alert.remove(), 3000));
    });




