// State Management
let borrowedBooks = JSON.parse(localStorage.getItem('libraryBooks')) || [
    { id: 201, title: "Moby Dick", author: "Herman Melville", daysLate: 14, isOverdue: true, dueDate: "Past Due" },
    { id: 203, title: "Brave New World", author: "Aldous Huxley", daysLate: 0, isOverdue: false, dueDate: "Standard Care" }
];
let transactionHistory = JSON.parse(localStorage.getItem('libraryHistory')) || [];

// UI Selectors
const borrowedListUI = document.getElementById('borrowed-list');
const historyListUI = document.getElementById('history-list');
const issueForm = document.getElementById('issue-form');

// Core LocalStorage Saver
function saveState() {
    localStorage.setItem('libraryBooks', JSON.stringify(borrowedBooks));
    localStorage.setItem('libraryHistory', JSON.stringify(transactionHistory));
}

// US 23: Handle Form Event Listener for Issuing Books
issueForm.addEventListener('submit', function(e) {
    e.preventDefault(); // Stop page reload

    const titleInput = document.getElementById('form-title').value;
    const authorInput = document.getElementById('form-author').value;
    const dateInput = document.getElementById('form-date').value;

    // Check if date is in the past to evaluate overdue logic dynamically
    const selectedDate = new Date(dateInput);
    const today = new Date();
    today.setHours(0,0,0,0);
    
    const isOverdue = selectedDate < today;
    let daysLate = 0;
    
    if (isOverdue) {
        const diffTime = Math.abs(today - selectedDate);
        daysLate = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }

    // Formulate new object payload
    const newIssue = {
        id: Date.now(), // Generate unique ID
        title: titleInput,
        author: authorInput,
        daysLate: daysLate,
        isOverdue: isOverdue,
        dueDate: selectedDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
    };

    // Push into app state lists
    borrowedBooks.push(newIssue);
    transactionHistory.push({
        title: newIssue.title,
        type: 'Issued',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });

    // Save and re-render system
    saveState();
    renderBooks();
    renderHistory();
    
    issueForm.reset(); // Clear input fields smoothly
});

// Render Borrowed List Pipeline
function renderBooks() {
    borrowedListUI.innerHTML = '';
    if (borrowedBooks.length === 0) {
        borrowedListUI.innerHTML = '<p class="text-sm text-slate-400 italic text-center py-4">No books currently checked out.</p>';
        return;
    }

    borrowedBooks.forEach(book => {
        const li = document.createElement('li');
        li.className = `flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl border transition-all gap-4 ${
            book.isOverdue ? 'bg-red-50 border-red-200' : 'bg-slate-50 border-slate-200'
        }`;
        
        li.innerHTML = `
            <div>
                <span class="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-full ${
                    book.isOverdue ? 'bg-red-600 text-white' : 'bg-slate-200 text-slate-600'
                }">${book.isOverdue ? 'Overdue' : 'Current'}</span>
                <h3 class="font-bold text-slate-800 text-base mt-1">${book.title}</h3>
                <p class="text-xs text-slate-500">${book.author}</p>
            </div>
            <div class="flex items-center justify-between sm:justify-end gap-4 border-t sm:border-t-0 pt-2 sm:pt-0">
                <span class="text-xs font-semibold ${book.isOverdue ? 'text-red-600' : 'text-indigo-600'}">
                    ${book.isOverdue ? `${book.daysLate} Days Late` : `Due: ${book.dueDate}`}
                </span>
                <button onclick="returnBook(${book.id})" class="bg-slate-800 hover:bg-red-600 text-white text-xs font-bold px-3 py-2 rounded-lg transition-all active:scale-95">
                    Return
                </button>
            </div>
        `;
        borrowedListUI.appendChild(li);
    });
}

// Process Book Return Transaction
function returnBook(bookId) {
    const bookIndex = borrowedBooks.findIndex(b => b.id === bookId);
    const targetBook = borrowedBooks[bookIndex];

    borrowedBooks.splice(bookIndex, 1);
    
    transactionHistory.push({
        title: targetBook.title,
        type: 'Returned',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });

    saveState();
    renderBooks();
    renderHistory();
}

// Render Consolidated Log Audit View
function renderHistory() {
    historyListUI.innerHTML = '';
    if (transactionHistory.length === 0) {
        historyListUI.innerHTML = '<p id="empty-history" class="text-sm text-slate-400 italic">No transactions recorded yet.</p>';
        return;
    }

    transactionHistory.forEach(item => {
        const li = document.createElement('li');
        li.className = "text-xs p-3 bg-slate-800 rounded-xl border border-slate-700 flex justify-between items-center";
        
        const badge = item.type === 'Issued' 
            ? `<span class="text-[10px] bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded border border-blue-500/30">Issued</span>`
            : `<span class="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/30">Returned</span>`;

        li.innerHTML = `
            <div class="truncate mr-2">
                <strong class="text-slate-100 block truncate">${item.title}</strong>
                <span class="text-[10px] text-slate-400">${item.timestamp}</span>
            </div>
            ${badge}
        `;
        historyListUI.prepend(li);
    });
}

// Initial Core Bootstrapping
renderBooks();
renderHistory();