// cypress/e2e/test_login.cy.js
describe('Login Test', () => {

    it('Successfully logs in with correct credentials', () => {
      cy.login(Cypress.env('username'), Cypress.env('password'))
    });
  
    it('Displays an error message for incorrect credentials', () => {
      cy.visit('/');

      // Fill in the login form with incorrect credentials
      cy.get('[data-cy=username]').type(Cypress.env('username'));
      cy.get('[data-cy=password]').type('incorrectPAssword');
  
      // Click the login button
      cy.get('[data-cy=login-button]').click();
  
      // Verify error message is displayed
      cy.get('[data-cy=error-message]').contains('Error: Invalid username or password');
    });

    it('Log Out', () => {
      cy.login(Cypress.env('username'), Cypress.env('password'))

      // log out
      cy.get('[data-cy="logOutLink"]').click()
      cy.get('[data-cy="logoutPage"]').contains('Log Out')
    });
  });
  