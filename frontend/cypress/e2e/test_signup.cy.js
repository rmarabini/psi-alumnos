// cypress/e2e/test_login.cy.js
describe('Login Test', () => {

  
    it('Displays an error message for incorrect credentials', () => {
      // clean database
      cy.delete_game()
      // print baseUrl in the console 
      // just to check that is there

      console.log("baseURl", Cypress.config().baseUrl)
      cy.visit('/sign-up');

      // create player
      cy.get('[data-cy=username]' ).type(Cypress.env('username'));
      cy.get('[data-cy=password1]').type(Cypress.env('password'));
      cy.get('[data-cy=password2]').type(Cypress.env('password'));
      cy.get('[data-cy=signup-button]').click();

      // home is also the log page
      cy.visit('/')
      // Fill in the login form
      cy.get('[data-cy=username]').type(Cypress.env('username'))
      cy.get('[data-cy=password]').type(Cypress.env('password'))
      cy.get('[data-cy=login-button]').click();

      // we should be redirected to /creategame
      cy.url().should('include', '/creategame')
      // Verify error message is displayed
      // cy.get('[data-cy=error-message]').contains('Error: Invalid username or password');
    });

  });
  
