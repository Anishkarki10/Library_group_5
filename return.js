document.getElementById('returnForm').addEventListener('submit', function(e) {
    e.preventDefault();

    // Capture values
    const bookId = document.getElementById('bookId').value;
    const memberId = document.getElementById('memberId').value;
    const messageDiv = document.getElementById('message');

    // Simple validation/simulation
    messageDiv.classList.remove('hidden', 'bg-green-100', 'text-green-700', 'bg-red-100', 'text-red-700');
    
    if (bookId && memberId) {
        // Simulate API call
        messageDiv.textContent = `Success! Book ${bookId} has been returned by member ${memberId}.`;
        messageDiv.classList.add('bg-green-100', 'text-green-700');
        document.getElementById('returnForm').reset();
    } else {
        messageDiv.textContent = "Please fill in all fields.";
        messageDiv.classList.add('bg-red-100', 'text-red-700');
    }
    
    messageDiv.classList.remove('hidden');
});