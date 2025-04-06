document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('createPetitionForm');

    // Event listener for creating a petition
    form.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        const title = document.getElementById('title').value.trim();
        const content = document.getElementById('content').value.trim();

        try {
            // Send API request to create a petition
            const response = await fetch('/create_petition', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, content }),
            });

            const result = await response.json();

            if (response.ok) {
                alert('Petition created successfully!');
                form.reset(); // Clear the form fields
                fetchPetitions(); // Reload petitions
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            console.error('Error creating petition:', error);
            alert('An error occurred while creating the petition. Please try again.');
        }
    });

    // Function to fetch and display all petitions
    async function fetchPetitions() {
        try {
            const response = await fetch('/petitions');
            const result = await response.json();

            if (response.ok) {
                const tableBody = document.getElementById('petitionsTableBody');
                tableBody.innerHTML = ''; // Clear the table before adding new data

                result.petitions.forEach((petition) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${petition.id}</td>
                        <td>${petition.title}</td>
                        <td>${petition.content}</td>
                        <td>${petition.status}</td>
                        <td>${petition.signatures}</td>
                        <td>
                            ${
                                petition.status === 'open'
                                    ? `<button class="btn btn-success btn-sm sign-btn" data-id="${petition.id}">Sign</button>`
                                    : 'Closed'
                            }
                        </td>
                    `;
                    tableBody.appendChild(row);
                });

                // Attach event listeners to "Sign" buttons
                document.querySelectorAll('.sign-btn').forEach((button) => {
                    button.addEventListener('click', async (event) => {
                        const petitionId = button.getAttribute('data-id');
                        await signPetition(petitionId);
                    });
                });
            } else {
                alert('Failed to fetch petitions. Please try again.');
            }
        } catch (error) {
            console.error('Error fetching petitions:', error);
        }
    }

    // Function to sign a petition
    async function signPetition(petitionId) {
        try {
            const response = await fetch(`/sign_petition/${petitionId}`, {
                method: 'POST',
            });

            const result = await response.json();

            if (response.ok) {
                alert('Petition signed successfully!');
                fetchPetitions(); // Reload petitions
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            console.error('Error signing petition:', error);
            alert('An error occurred while signing the petition. Please try again.');
        }
    }

    // Fetch petitions on page load
    fetchPetitions();
});
