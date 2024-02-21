document.addEventLister('DOMContentLoaded', function() { // Waiting for the DOM to be fully loaded
    // Adding event listener to delete buttons
    var deleteButtons = document.querySelectorAll('.delete-button'); // Selecting all delete buttons

    deleteButtons.forEach(function(button) { // Iterating over each delete button
        button.addEventListener('click', function() { // Adding event listener to each delete button
            // Displaying confirmation dialog
            var confirmation = confirm('Are you sure you want to delete this invoice?'); 

            // Proceeding with deletion, if user confirms
            if (confirmation) { 
                // Getting invoice ID from data-id attribute
                var invoiceId = button.getAttribute('data-id'); 

                // Sending AJAX request to server to delete the invoice
                fetch('/delete' + invoiceId, { // Sending request to /delete/<invoiceId>
                    method: 'POST', // Using POST method
                })
                .then(response => response.json()) // Parsing response as JSON
                .then(data => { // Handling the parsed data
                    if (data.success) { // Checking if the request was successful
                        location.reload(); // Reloading the page
                    } else {  // Handling error
                        alert('Error: ' + data.message); // Displaying error message
                    }
                })
                .catch(error => { // Handling errors
                    console.error('Error: ', error); // Logging error to the console
                    alert('An error occurred while deleting the invoice.'); // Displaying error message
                });
            }
        });
    });
});