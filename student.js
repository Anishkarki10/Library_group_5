const books = [
    { id: 1, title: "Introduction to Algorithms", author: "Thomas Cormen", genre: "Computer Science", available: true, total: 5, available_count: 2, location: "Shelf A-12" },
    { id: 2, title: "Clean Code", author: "Robert Martin", genre: "Programming", available: true, total: 3, available_count: 1, location: "Shelf B-05" },
    { id: 3, title: "Design Patterns", author: "Gang of Four", genre: "Software Engineering", available: false, total: 4, available_count: 0, location: "Shelf A-15" },
    { id: 4, title: "The Pragmatic Programmer", author: "Andy Hunt", genre: "Programming", available: true, total: 6, available_count: 3, location: "Shelf B-08" },
    { id: 5, title: "Data Structures and Algorithms", author: "Mark Weiss", genre: "Computer Science", available: true, total: 4, available_count: 2, location: "Shelf A-10" },
    { id: 6, title: "Artificial Intelligence: A Modern Approach", author: "Stuart Russell", genre: "AI/ML", available: false, total: 3, available_count: 0, location: "Shelf C-03" }
  ];
  
  const myBorrowings = [
    { id: 1, title: "Design Patterns", author: "Gang of Four", dueDate: "2026-05-05", status: "active" },
    { id: 2, title: "Artificial Intelligence", author: "Stuart Russell", dueDate: "2026-04-28", status: "overdue" }
  ];
  
  const readingHistory = [
    { id: 1, title: "Clean Architecture", author: "Robert Martin", returnedDate: "2026-04-20" },
    { id: 2, title: "JavaScript: The Good Parts", author: "Douglas Crockford", returnedDate: "2026-04-15" }
  ];
  
  const bookIcon = `
    <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
      <path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5z"></path>
    </svg>
  `;
  
  const bookGrid = document.getElementById("bookGrid");
  const searchInput = document.getElementById("searchInput");
  const genreSelect = document.getElementById("genreSelect");
  
  function renderBooks() {
    const searchText = searchInput.value.toLowerCase();
    const selectedGenre = genreSelect.value;
  
    const filteredBooks = books.filter(book => {
      const matchesSearch =
        book.title.toLowerCase().includes(searchText) ||
        book.author.toLowerCase().includes(searchText);
  
      const matchesGenre =
        selectedGenre === "all" || book.genre === selectedGenre;
  
      return matchesSearch && matchesGenre;
    });
  
    bookGrid.innerHTML = "";
  
    if (filteredBooks.length === 0) {
      bookGrid.innerHTML = `<p>No books found.</p>`;
      return;
    }
  
    filteredBooks.forEach(book => {
      const card = document.createElement("div");
      card.className = "book-card";
  
      card.innerHTML = `
        <div class="book-inner">
          <div class="book-cover">${bookIcon}</div>
  
          <div class="book-info">
            <h3 title="${book.title}">${book.title}</h3>
            <p>${book.author}</p>
            <span class="genre-tag">${book.genre}</span>
  
            <div class="book-actions">
              <span class="status ${book.available ? "available" : "unavailable"}">
                ${book.available ? "Available" : "Checked Out"}
              </span>
  
              <button class="reserve-btn ${book.available ? "" : "disabled"}" ${book.available ? "" : "disabled"}>
                ${book.available ? "Reserve" : "Waitlist"}
              </button>
            </div>
          </div>
        </div>
      `;
  
      bookGrid.appendChild(card);
    });
  }
  
  function renderBorrowings() {
    const container = document.getElementById("borrowingsList");
    container.innerHTML = "";
  
    myBorrowings.forEach(book => {
      const item = document.createElement("div");
      item.className = "list-item";
  
      item.innerHTML = `
        <div class="list-left">
          <div class="small-cover">${bookIcon}</div>
          <div>
            <div class="list-title">${book.title}</div>
            <div class="list-author">${book.author}</div>
          </div>
        </div>
  
        <div class="list-right">
          <div class="list-label">Due Date</div>
          <div class="due-date ${book.status === "overdue" ? "red-text" : ""}">${book.dueDate}</div>
          ${book.status === "overdue" ? `<span class="overdue-badge">Overdue</span>` : ""}
        </div>
      `;
  
      container.appendChild(item);
    });
  }
  
  function renderHistory() {
    const container = document.getElementById("historyList");
    container.innerHTML = "";
  
    readingHistory.forEach(book => {
      const item = document.createElement("div");
      item.className = "list-item";
  
      item.innerHTML = `
        <div class="list-left">
          <div class="small-cover history-cover">${bookIcon}</div>
          <div>
            <div class="list-title">${book.title}</div>
            <div class="list-author">${book.author}</div>
          </div>
        </div>
  
        <div class="list-right">
          <div class="list-label">Returned</div>
          <div class="due-date">${book.returnedDate}</div>
        </div>
      `;
  
      container.appendChild(item);
    });
  }
  
  document.querySelectorAll(".nav-btn").forEach(button => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".nav-btn").forEach(btn => btn.classList.remove("active"));
      document.querySelectorAll(".page").forEach(page => page.classList.remove("active-page"));
  
      button.classList.add("active");
      document.getElementById(button.dataset.page).classList.add("active-page");
    });
  });
  
  searchInput.addEventListener("input", renderBooks);
  genreSelect.addEventListener("change", renderBooks);
  
  renderBooks();
  renderBorrowings();
  renderHistory();