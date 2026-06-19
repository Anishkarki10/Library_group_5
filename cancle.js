/**
 * Processes clean client-side dynamic content querying adjustments on layout rows
 */
function filterReservations() {
  const userSearchInput = document.getElementById('reservationSearch').value.toLowerCase();
  const visibleDataRows = document.querySelectorAll('#reservationsTable tbody .hold-row');
  let matchedMatchesCounter = 0;

  visibleDataRows.forEach(row => {
    const assetTitle = row.querySelector('.data-title').textContent.toLowerCase();
    const assetAuthor = row.querySelector('.data-author').textContent.toLowerCase();
    
    const evaluationMatch = assetTitle.includes(userSearchInput) || assetAuthor.includes(userSearchInput);

    if (evaluationMatch) {
      row.style.display = "";
      matchedMatchesCounter++;
    } else {
      row.style.display = "none";
    }
  });

  document.getElementById('resultsCounter').textContent = `Showing ${matchedMatchesCounter} holds`;
}

/**
 * Handles state transitions for removing/canceling an active student reservation hold
 * @param {HTMLElement} selectedBtnCtx - Context identifier reference of target button clicked
 */
function triggerCancellation(selectedBtnCtx) {
  const selectedRowContext = selectedBtnCtx.closest('.hold-row');
  const targetBadgeElement = selectedRowContext.querySelector('.hold-badge');
  const dynamicTotalCounter = document.getElementById('reservationCount');

  // 1. Transition status badges to showcase item cancellation instantly
  targetBadgeElement.textContent = "Cancelled Hold";
  targetBadgeElement.className = "px-2 py-0.5 rounded text-xs font-bold bg-slate-100 text-slate-400 border border-slate-200 hold-badge animate-pulse";

  // 2. Disable layout buttons cleanly to lock action modifications
  selectedBtnCtx.textContent = "Removed";
  selectedBtnCtx.disabled = true;
  selectedBtnCtx.className = "bg-slate-200 text-slate-400 text-xs font-semibold px-3 py-1.5 rounded-lg cursor-not-allowed cancel-btn";

  // 3. Decrement overall dashboard active record counts
  let activeHolds = parseInt(dynamicTotalCounter.textContent, 10) || 0;
  if (activeHolds > 0) {
    dynamicTotalCounter.textContent = activeHolds - 1;
  }
}