/**
 * Direct real-time evaluation engine tracking filtering queries against catalog lists
 */
function filterInventoryTable() {
  const userQuery = document.getElementById('inventorySearch').value.toLowerCase();
  const catalogRows = document.querySelectorAll('#inventoryTable tbody .catalog-row');
  let itemsCountTracker = 0;

  catalogRows.forEach(row => {
    const titleText = row.querySelector('.lookup-title').textContent.toLowerCase();
    const authorText = row.querySelector('.lookup-author').textContent.toLowerCase();
    const isbnCode = row.querySelector('.data-isbn').textContent.toLowerCase();
    
    // Evaluate if the input pattern intersects any database descriptors
    const recordMatches = titleText.includes(userQuery) || authorText.includes(userQuery) || isbnCode.includes(userQuery);

    if (recordMatches) {
      row.style.display = "";
      itemsCountTracker++;
    } else {
      row.style.display = "none";
    }
  });

  document.getElementById('tableStateCounter').textContent = `Showing ${itemsCountTracker} catalog listings`;
}

/**
 * Transitions targeted assets through double-check confirm flags to execute record deletion safely
 * @param {HTMLElement} btnInstanceContext - Click context target element context
 */
function stageItemDeletion(btnInstanceContext) {
  const targetRow = btnInstanceContext.closest('.catalog-row');
  const metricCounter = document.getElementById('inventoryCount');

  // Multi-state double check logic loop evaluation blocks
  if (btnInstanceContext.textContent === "Delete") {
    // Stage 1: Change to confirm state
    btnInstanceContext.textContent = "Confirm?";
    btnInstanceContext.className = "bg-rose-600 text-white text-xs font-bold px-3 py-1.5 rounded-lg transition-colors cursor-pointer shadow-xs delete-trigger-btn animate-pulse";
    
    // Auto reset to default state after 3.5 seconds if action is abandoned
    btnInstanceContext.dataset.timeoutId = setTimeout(() => {
      btnInstanceContext.textContent = "Delete";
      btnInstanceContext.className = "bg-slate-100 hover:bg-rose-50 text-slate-600 hover:text-rose-600 text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors cursor-pointer border border-slate-200 hover:border-rose-200 shadow-xs delete-trigger-btn";
    }, 3500);

  } else if (btnInstanceContext.textContent === "Confirm?") {
    // Stage 2: Finalize deletion process execution
    clearTimeout(parseInt(btnInstanceContext.dataset.timeoutId, 10));
    
    // Smooth fade out layout effect transition handling
    targetRow.style.transition = "all 0.3s ease";
    targetRow.style.opacity = "0";
    targetRow.style.transform = "translateX(20px)";

    setTimeout(() => {
      targetRow.remove();
      
      // Sync metrics counter data flags
      let itemsRemaining = document.querySelectorAll('#inventoryTable tbody .catalog-row').length;
      metricCounter.textContent = itemsRemaining;
      
      // Recalculate context results total numbers
      filterInventoryTable();
    }, 3000);
  }
}