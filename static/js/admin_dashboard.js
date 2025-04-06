document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('petitionsTableBody');
    const respondForm = document.getElementById('respondForm');
    const responseText = document.getElementById('responseText');
    const respondPetitionId = document.getElementById('respondPetitionId');

    async function fetchPetitions() {
        try {
            const response = await fetch('/admin/view_petitions');
            const result = await response.json();

            if (response.ok) {
                tableBody.innerHTML = ''; // Clear the table

                result.petitions.forEach((petition) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${petition.id}</td>
                        <td>${petition.title}</td>
                        <td>${petition.content}</td>
                        <td>${petition.status}</td>
                        <td>${petition.signatures}</td>
                        <td>${petition.response}</td>
                      <td>
    <button class="btn btn-sm btn-primary respond-btn" data-id="${petition.id}" data-bs-toggle="modal" data-bs-target="#respondModal">Respond</button>
</td>

                    `;
                    tableBody.appendChild(row);
                });

                attachRespondHandlers(); // Attach event listeners to buttons
            } else {
                alert(`Failed to fetch petitions: ${result.error}`);
            }
        } catch (error) {
            console.error('Error fetching petitions:', error);
            alert('An error occurred while fetching petitions.');
        }
    }

    function attachRespondHandlers() {
        const respondButtons = document.querySelectorAll('.respond-btn');
        respondButtons.forEach((button) => {
            button.addEventListener('click', () => {
                const petitionId = button.getAttribute('data-id');
                respondPetitionId.value = petitionId;
                responseText.value = '';
            });
        });
    }

    fetchPetitions(); // Fetch petitions on page load
});


    // Submit response to petition
    respondForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const petitionId = respondPetitionId.value;
        const responseContent = responseText.value;

        if (!responseContent.trim()) {
            alert('Response cannot be empty.');
            return;
        }

        try {
            const response = await fetch(`/admin/respond_petition/${petitionId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ response: responseContent }),
            });

            const result = await response.json();

            if (response.ok) {
                alert('Response submitted successfully!');
                fetchPetitions(); // Refresh the table
                const modal = bootstrap.Modal.getInstance(document.getElementById('respondModal'));
                modal.hide(); // Close the modal
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            console.error('Error submitting response:', error);
            alert('An error occurred while submitting the response.');
        }
    });

    // Fetch petitions on page load
    fetchPetitions();

