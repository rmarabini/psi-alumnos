// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })

// "export PYTHON3=/home/roberto/Docencia/PSI/psi/2023_24/psi2023_24/venv/bin/python\n" +
// 
// fill free to modify the path to python3 and manage.py"
const PYTHON = "/home/roberto/Docencia/psi/2023_24/venv/bin/python"
const MANAGE = "/home/roberto/Docencia/psi/2023_24/tutorial/manage.py"

Cypress.Commands.add('login', (username, password) => {
    // create test users
    var command = "# create user if it does not exist" +
                "# fill free to modify the path to python3 and manage.py" +
                "\n" +
                "export _PYTHON=" + PYTHON + "\n" +
                "export _MANAGE=" + MANAGE + "\n" +
                "# nothing to modify before this line\n" +
                "\n" +
                "cat <<EOF | ${_PYTHON} ${_MANAGE} shell\n" +
                "from django.contrib.auth import get_user_model\n" +
                "password = 'sacacorchos'\n" +
                "email = 'user1@example.com'\n" +
                "username = email\n" +
                "email2 = 'user1@example.com'\n" +
                "\n" +
                "User = get_user_model()  # get the currently active user model,\n" +
                "\n" +
                "if not User.objects.filter(username=username).exists():\n" +
                    "    User.objects.create_user(username, email, password)\n" +
                "else:\n" +
                    "    print(f'User {username} exists already, not created')\n" +
                "EOF\n"
    cy.exec(command)
    // home is also the log page
    cy.visit('/')
    // Fill in the login form
    console.log("username", username)
    cy.get('[data-cy=username]').type(username)
  
    // causes the form to submit
    cy.get('[data-cy=password]').type(password)

    // Click the login button
    // we may have used 
    // {enter} which causes the form to submit
    // cy.get('input[name=password]').type(`${password}{enter}`, { log: false })

    cy.get('[data-cy=login-button]').click();

    // we should be redirected to /creategame
    cy.url().should('include', '/creategame')
  })
