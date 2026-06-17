// Simulated database with a mix of overdue and active books
let borrowedBooks = [
    { id: 201, title: "Moby Dick", author: "Herman Melville", daysLate: 14, isOverdue: true },
    { id: 202, title: "The Catcher in the Rye", author: "J.D. Salinger", daysLate: 3, isOverdue: true },
    { id: 203, title: "Brave New World", author: "Aldous Huxley", daysLate: 0, isOverdue: false, dueDate: "In 4 Days" },
    { id: 204, title: "Dune", author: "Frank Herbert", daysLate: 0, isOverdue: false, dueDate: "In 9 Days" }
];

const borrowedListUI = document.getElementById('borrowed-list');
const historyListUI = document.getElementById('history-list');
const emptyHistoryMsg = document.getElementById('empty-history');

// Core UI builder
function renderBooks() {
    borrowedListUI.innerHTML = '';
    
    if (borrowedBooks.length === 0) {
        borrowedListUI.innerHTML = `
            <div class="text-center py-8 bg-emerald-50 rounded-xl border border-dashed border-emerald-300">
                <p class="text-emerald-700 font-medium">All clear! No overdue or borrowed books remaining.</p>
            </div>`;
        return;
    }

    borrowedBooks.forEach(book => {
        const li = document.createElement('li');
        
        // Dynamic styling changes conditionally if the book is overdue
        if (book.isOverdue) {
            li.className = "flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-red-50 rounded-xl border border-red-200 hover:bg-red-100/70 transition-all gap-4";
        } else {
            li.className = "flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-indigo-200 transition-all gap-4";
        }
        
        // Build the inside card structure using conditional layouts
        li.innerHTML = `
            <div class="flex flex-col sm:flex-row sm:items-center gap-3">
                ${book.isOverdue 
                    ? `<span class="self-start sm:self-auto text-[11px] font-bold tracking-wider uppercase bg-red-600 text-white px-2 py-0.5 rounded-full shadow-sm shadow-red-200">OVERDUE</span>` 
                    : `<span class="self-start sm:self-auto text-[11px] font-bold tracking-wider uppercase bg-slate-200 text-slate-600 px-2 py-0.5 rounded-full">Current</span>`
                }
                <div>
                    <h3 class="font-bold text-slate-800 text-base">${book.title}</h3>
                    <p class="text-xs text-slate-500">${book.author}</p>
                </div>
            </div>
            
            <div class="flex items-center justify-between sm:justify-end gap-6 border-t sm:border-t-0 pt-2 sm:pt-0 border-slate-200">
                <span class="text-xs font-semibold ${book.isOverdue ? 'text-red-600' : 'text-indigo-600'}">
                    ${book.isOverdue ? `${book.daysLate} Days Late` : `Due: ${book.dueDate}`}
                </span>
                <button 
                    onclick="returnBook(${book.id})"
                    class="w-24 bg-slate-800 hover:bg-indigo-600 text-white text-xs font-bold py-2 rounded-lg transition-all shadow-sm active:scale-95">
                    Process
                </button>
            </div>
        `;
        borrowedListUI.appendChild(li);
    });
}

// Handler execution
function returnBook(bookId) {
    const bookIndex = borrowedBooks.findIndex(b => b.id === bookId);
    const targetBook = borrowedBooks[bookIndex];

    borrowedBooks.splice(bookIndex, 1);

    logToHistory(targetBook);
    renderBooks();
}

// Log updater
function logToHistory(book) {
    if (document.getElementById('empty-history')) {
        emptyHistoryMsg.remove();
    }

    const item = document.createElement('li');
    item.className = "text-xs p-3 bg-slate-800 rounded-xl border border-slate-700 flex justify-between items-center animate-fadeIn";
    
    // Track fine collection states visually inside our panel history
    const statusBadge = book.isOverdue 
        ? `<span class="text-[10px] bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded border border-amber-500/30">Fine Assessed</span>`
        : `<span class="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/30">Returned Safe</span>`;

    item.innerHTML = `
        <div class="truncate mr-2">
            <span class="text-slate-400">Processed:</span>
            <strong class="text-slate-100 block truncate">${book.title}</strong>
        </div>
        ${statusBadge}
    `;
    
    historyListUI.prepend(item);
}

// Initialize system state loop
renderBooks();v