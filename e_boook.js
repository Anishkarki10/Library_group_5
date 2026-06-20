/**
 * Direct search evaluation engine mapping queries to card nodes
 */
function filterEbooks() {
  const query = document.getElementById('ebookSearch').value.toLowerCase().trim();
  const mediaCards = document.querySelectorAll('#ebookGrid .ebook-card');
  let matchCounter = 0;

  mediaCards.forEach(card => {
    const titleText = card.querySelector('.ebook-title').textContent.toLowerCase();
    const authorText = card.querySelector('.ebook-author').textContent.toLowerCase();

    const evaluationMatch = titleText.includes(query) || authorText.includes(query);

    if (evaluationMatch) {
      card.style.display = "flex";
      matchCounter++;
    } else {
      card.style.display = "none";
    }
  });

  document.getElementById('ebookCounterDisplay').textContent = `Showing ${matchCounter} digital media files`;
}

/**
 * Simulates micro-animations for download triggers locally
 * @param {HTMLElement} elementRef - Button click item context context
 * @param {string} fileName - File string tag targeted
 */
function handleEbookDownload(elementRef, fileName) {
  // Prevent duplicate double clicks during active streaming simulation
  if (elementRef.dataset.loading === "true") return;
  elementRef.dataset.loading = "true";

  // Change styles to indicate file request processing layout shifts
  elementRef.className = "bg-slate-200 text-slate-500 text-xs font-semibold px-3 py-1.5 rounded-lg cursor-not-allowed flex items-center gap-1 animate-pulse";
  elementRef.innerHTML = `
    <svg class="animate-spin h-3 w-3 text-slate-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    Fetching File...
  `;

  // Restore interactive success download components upon timeout completions
  setTimeout(() => {
    elementRef.dataset.loading = "false";
    elementRef.className = "bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors cursor-pointer flex items-center gap-1";
    elementRef.innerHTML = `
      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"></path></svg>
      Saved Local
    `;
    
    console.log(`Successfully completed background stream delivery pipeline asset routing context key: ${fileName}`);
  }, 1800);
}