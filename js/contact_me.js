$(function() {
    // ...

    $("input,textarea").jqBootstrapValidation({
        // ...

        submitSuccess: function($form, event) {
            event.preventDefault(); // prevent default submit behavior
            // get values from FORM
            var name = $("input#name").val();
            var email = $("input#email").val();
            var phone = $("input#phone").val();
            var message = $("textarea#message").val();
            var firstName = name; // For Success/Failure Message
            // Check for white space in name for Success/Fail message
            if (firstName.indexOf(' ') >= 0) {
                firstName = name.split(' ').slice(0, -1).join(' ');
            }

            // Use fetch to make the POST request to the AWS API
            fetch('https://j1mxvebrqe.execute-api.sa-east-1.amazonaws.com/Prod/users', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    phone: phone,
                    message: message
                }),
                credentials: 'include' // O 'same-origin' si tu frontend y API están en el mismo dominio
            })
            .then((response) => {
                if (response.ok) {
                    // Success message
                    $('#success').html("<div class='alert alert-success'>");
                    $('#success > .alert-success').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
                        .append("</button>");
                    $('#success > .alert-success')
                        .append("<strong>Your message has been sent. </strong>");
                    $('#success > .alert-success')
                        .append('</div>');

                    // Clear all fields
                    $('#contactForm').trigger("reset");
                } else {
                    // Fail message
                    $('#success').html("<div class='alert alert-danger'>");
                    $('#success > .alert-danger').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
                        .append("</button>");
                    $('#success > .alert-danger').append("<strong>Sorry " + firstName + ", it seems that my mail server is not responding. Please try again later!");
                    $('#success > .alert-danger').append('</div>');

                    // Clear all fields
                    $('#contactForm').trigger("reset");
                }
            })
            .catch((error) => {
                // Error handling
                console.error('Error:', error);
            });
        },

        // ...
    });

    // ...
});

/*When clicking on Full hide fail/success boxes */
$('#name').focus(function() {
    $('#success').html('');
});
