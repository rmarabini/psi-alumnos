// cypress/e2e/test_login.cy.js
describe("Login Test", () => {
  it("Log-in with correct credentials", () => {
    // const python = Cypress.env('python')
    // const manage = Cypress.env('manage')
    cy.login(Cypress.env("username"), Cypress.env("password"));
    // This test may fail if repeated several times with no logout
  });

  it("When Log-in, display an error message if incorrect credentials are provided", () => {
    cy.visit("/");
    // go to log page
    cy.get("[data-cy=login-cypress-test]").click();

    // Fill in the login form with incorrect credentials
    cy.get("[data-cy=username]").type(Cypress.env("username"));
    cy.get("[data-cy=password]").type("incorrectPAssword");

    // Click the login button
    cy.get("[data-cy=login-button]").click();

    // Verify error message is displayed
    cy.get("[data-cy=error-message]").contains(
      "Error: Invalid username or password"
    );
  });

  it("check that Log Out is working", () => {
    cy.login(Cypress.env("username"), Cypress.env("password"));

    cy.get('[data-cy="logout-cypress-test"]').click();
    cy.get('[data-cy="logoutPage"]').contains("Log Out");
  });
});
