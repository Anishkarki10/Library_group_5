const books = [
    { id: 1, title: "Introduction to Algorithms", author: "Thomas Cormen", genre: "Computer Science", available: true, total: 5, available_count: 2, location: "Shelf A-12" },
    { id: 2, title: "Clean Code", author: "Robert Martin", genre: "Programming", available: true, total: 3, available_count: 1, location: "Shelf B-05" },
    { id: 3, title: "Design Patterns", author: "Gang of Four", genre: "Software Engineering", available: false, total: 4, available_count: 0, location: "Shelf A-15" },
    { id: 4, title: "The Pragmatic Programmer", author: "Andy Hunt", genre: "Programming", available: true, total: 6, available_count: 3, location: "Shelf B-08" },
    { id: 5, title: "Data Structures and Algorithms", author: "Mark Weiss", genre: "Computer Science", available: true, total: 4, available_count: 2, location: "Shelf A-10" },
    { id: 6, title: "Artificial Intelligence: A Modern Approach", author: "Stuart Russell", genre: "AI/ML", available: false, total: 3, available_count: 0, location: "Shelf C-03" }
  ];
  
  const activeLoans = [
    { id: 1, student: "Alice Johnson", book: "Design Patterns", checkoutDate: "2026-04-20", dueDate: "2026-05-05", status: "active" },
    { id: 2, student: "Bob Smith", book: "Artificial Intelligence", checkoutDate: "2026-04-13", dueDate: "2026-04-28", status: "overdue" },
    { id: 3, student: "Carol White", book: "Database Systems", checkoutDate: "2026-04-25", dueDate: "2026-05-10", status: "active" }
  ];
  
  const returnedLoans = [
    { id: 4, student: "David Lee", book: "Clean Code", checkoutDate: "2026-03-18", dueDate: "2026-04-02", status: "returned" },
    { id: 5, student: "Eva Brown", book: "The Pragmatic Programmer", checkoutDate: "2026-03-22", dueDate: "2026-04-06", status: "returned" }
  ];
  
  const popularBooksData = [
    { name: "Clean Code", count: 45 },
    { name: "Design Patterns", count: 38 },
    { name: "Algorithms", count: 35 },
    { name: "AI Modern Approach", count: 32 },
    { name: "Pragmatic Programmer", count: 28 }
  ];
  
  const circulationTrendData = [
    { month: "Dec", checkouts: 120 },
    { month: "Jan", checkouts: 145 },
    { month: "Feb", checkouts: 160 },
    { month: "Mar", checkouts: 155 },
    { month: "Apr", checkouts: 180 }
  ];
  
  document.querySelectorAll(".nav-btn").forEach(button => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".nav-btn").forEach(btn => btn.classList.remove("active"));
      document.querySelectorAll(".page").forEach(page => page.classList.remove("active-page"));
  
      button.classList.add("active");
      document.getElementById(button.dataset.page).classList.add("active-page");
    });
  });
  
  function renderPopularBooksChart() {
    const chart = document.getElementById("popularBooksChart");
    const maxCount = Math.max(...popularBooksData.map(item => item.count));
  
    chart.innerHTML = "";
  
    popularBooksData.forEach(item => {
      const height = (item.count / maxCount) * 220;
  
      const barItem = document.createElement("div");
      barItem.className = "bar-item";
  
      barItem.innerHTML = `
        <div class="bar" style="height: ${height}px;">
          <span>${item.count}</span>
        </div>
        <div class="bar-label">${item.name}</div>
      `;
  
      chart.appendChild(barItem);
    });
  }
  
  function renderCirculationLineChart() {
    const svg = document.getElementById("circulationLineChart");
    const width = 520;
    const height = 300;
    const padding = 35;
  
    const maxValue = Math.max(...circulationTrendData.map(item => item.checkouts));
    const minValue = Math.min(...circulationTrendData.map(item => item.checkouts));
  
    const points = circulationTrendData.map((item, index) => {
      const x = padding + (index * ((width - padding * 2) / (circulationTrendData.length - 1)));
      const y = height - padding - ((item.checkouts - minValue) / (maxValue - minValue)) * (height - padding * 2);
      return { x, y, ...item };
    });
  
    const polylinePoints = points.map(point => `${point.x},${point.y}`).join(" ");
  
    svg.innerHTML = `
      <polyline points="${polylinePoints}" fill="none" stroke="#16a34a" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></polyline>
      ${points.map(point => `
        <circle cx="${point.x}" cy="${point.y}" r="6" fill="#16a34a"></circle>
        <text x="${point.x}" y="${point.y - 14}" text-anchor="middle" font-size="13" font-weight="700" fill="#111827">${point.checkouts}</text>
        <text x="${point.x}" y="286" text-anchor="middle" font-size="13" fill="#6b7280">${point.month}</text>
      `).join("")}
    `;
  }
  
  function renderInventoryTable() {
    const tbody = document.getElementById("inventoryTable");
    tbody.innerHTML = "";
  
    books.forEach(book => {
      const row = document.createElement("tr");
  
      row.innerHTML = `
        <td>${book.id}</td>
        <td class="book-title">${book.title}</td>
        <td>${book.author}</td>
        <td>${book.genre}</td>
        <td>${book.total}</td>
        <td>
          <span class="badge ${book.available_count > 0 ? "badge-green" : "badge-red"}">
            ${book.available_count}
          </span>
        </td>
        <td>${book.location}</td>
        <td>
          <button class="action-link edit-link">Edit</button>
          <button class="action-link delete-link">Delete</button>
        </td>
      `;
  
      tbody.appendChild(row);
    });
  }
  
  function renderCirculationTable(filter = "all") {
    const tbody = document.getElementById("circulationTable");
  
    let loans = [...activeLoans];
  
    if (filter === "overdue") {
      loans = activeLoans.filter(loan => loan.status === "overdue");
    }
  
    if (filter === "returned") {
      loans = returnedLoans;
    }
  
    tbody.innerHTML = "";
  
    loans.forEach(loan => {
      const isReturned = loan.status === "returned";
      const isOverdue = loan.status === "overdue";
  
      const row = document.createElement("tr");
  
      row.innerHTML = `
        <td>${loan.id}</td>
        <td class="student-name">${loan.student}</td>
        <td>${loan.book}</td>
        <td>${loan.checkoutDate}</td>
        <td>${loan.dueDate}</td>
        <td>
          <span class="badge ${isOverdue ? "badge-red" : "badge-green"}">
            ${isReturned ? "Returned" : isOverdue ? "Overdue" : "Active"}
          </span>
        </td>
        <td>
          ${isReturned
            ? `<button class="action-link edit-link">View</button>`
            : `<button class="action-link reminder-link">Send Reminder</button>
               <button class="action-link return-link">Mark Returned</button>`
          }
        </td>
      `;
  
      tbody.appendChild(row);
    });
  }
  
  document.querySelectorAll(".tab-btn").forEach(button => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active-tab"));
      button.classList.add("active-tab");
      renderCirculationTable(button.dataset.filter);
    });
  });
  
  document.getElementById("exportInventoryBtn").addEventListener("click", () => {
    const headers = ["ID", "Title", "Author", "Genre", "Total", "Available", "Location"];
    const rows = books.map(book => [
      book.id,
      book.title,
      book.author,
      book.genre,
      book.total,
      book.available_count,
      book.location
    ]);
  
    const csv = [headers, ...rows]
      .map(row => row.map(value => `"${String(value).replaceAll('"', '""')}"`).join(","))
      .join("\\n");
  
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
  
    const link = document.createElement("a");
    link.href = url;
    link.download = "library-inventory.csv";
    link.click();
  
    URL.revokeObjectURL(url);
  });
  
  renderPopularBooksChart();
  renderCirculationLineChart();
  renderInventoryTable();
  renderCirculationTable();