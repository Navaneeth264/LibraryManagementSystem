// ==========================================
// Library Management System - JavaScript
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    // --------------------------------------
    // LOGIN VALIDATION
    // --------------------------------------

    const loginForm = document.getElementById("loginForm");

    if (loginForm) {

        loginForm.addEventListener("submit", function (event) {

            const username =
                document.getElementById("username");

            const password =
                document.getElementById("password");


            if (username.value.trim() === "") {

                alert("Please enter your username.");

                event.preventDefault();

                username.focus();

                return;
            }


            if (password.value.trim() === "") {

                alert("Please enter your password.");

                event.preventDefault();

                password.focus();

                return;
            }

        });
    }


    // --------------------------------------
    // REGISTRATION VALIDATION
    // --------------------------------------

    const registerForm =
        document.getElementById("registerForm");

    if (registerForm) {

        registerForm.addEventListener("submit", function (event) {

            const username =
                document.getElementById("username");

            const password =
                document.getElementById("password");

            const confirmPassword =
                document.getElementById("confirm_password");


            // Username validation
            if (username.value.trim().length < 3) {

                alert(
                    "Username must contain at least 3 characters."
                );

                event.preventDefault();

                username.focus();

                return;
            }


            // Password validation
            if (password.value.length < 6) {

                alert(
                    "Password must contain at least 6 characters."
                );

                event.preventDefault();

                password.focus();

                return;
            }


            // Confirm password
            if (password.value !== confirmPassword.value) {

                alert(
                    "Passwords do not match."
                );

                event.preventDefault();

                confirmPassword.focus();

                return;
            }

        });
    }


    // --------------------------------------
    // SHOW / HIDE PASSWORD
    // --------------------------------------

    const passwordFields =
        document.querySelectorAll(
            'input[type="password"]'
        );


    passwordFields.forEach(function (password) {

        const button =
            document.createElement("button");

        button.type = "button";

        button.textContent =
            "👁️ Show Password";

        button.style.marginTop = "8px";
        button.style.padding = "8px 12px";
        button.style.border = "none";
        button.style.borderRadius = "6px";
        button.style.cursor = "pointer";


        password.parentNode.appendChild(button);


        button.addEventListener("click", function () {

            if (password.type === "password") {

                password.type = "text";

                button.textContent =
                    "🙈 Hide Password";

            } else {

                password.type = "password";

                button.textContent =
                    "👁️ Show Password";
            }

        });

    });


    // --------------------------------------
    // ADD / UPDATE BOOK VALIDATION
    // --------------------------------------

    const bookForms =
        document.querySelectorAll(
            ".form-container form"
        );


    bookForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const title =
                document.getElementById("title");

            const author =
                document.getElementById("author");


            if (title && title.value.trim() === "") {

                alert(
                    "Please enter the book title."
                );

                event.preventDefault();

                title.focus();

                return;
            }


            if (author && author.value.trim() === "") {

                alert(
                    "Please enter the author name."
                );

                event.preventDefault();

                author.focus();

                return;
            }

        });

    });


    // --------------------------------------
    // DELETE CONFIRMATION
    // --------------------------------------

    const deleteButtons =
        document.querySelectorAll(".delete-btn");


    deleteButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            const confirmed =
                confirm(
                    "Are you sure you want to delete this book?"
                );


            if (!confirmed) {

                event.preventDefault();

            }

        });

    });


    // --------------------------------------
    // ISSUE CONFIRMATION
    // --------------------------------------

    const issueButtons =
        document.querySelectorAll(".issue-btn");


    issueButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            const confirmed =
                confirm(
                    "Do you want to issue this book?"
                );


            if (!confirmed) {

                event.preventDefault();

            }

        });

    });


    // --------------------------------------
    // RETURN CONFIRMATION
    // --------------------------------------

    const returnButtons =
        document.querySelectorAll(".return-btn");


    returnButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            const confirmed =
                confirm(
                    "Do you want to return this book?"
                );


            if (!confirmed) {

                event.preventDefault();

            }

        });

    });


    // --------------------------------------
    // SEARCH VALIDATION
    // --------------------------------------

    const searchForm =
        document.querySelector(".search-form");


    if (searchForm) {

        searchForm.addEventListener(
            "submit",
            function (event) {

                const searchInput =
                    searchForm.querySelector(
                        'input[name="keyword"]'
                    );


                if (searchInput.value.trim() === "") {

                    alert(
                        "Please enter a book title or author."
                    );

                    event.preventDefault();

                    searchInput.focus();

                }

            }
        );

    }

});