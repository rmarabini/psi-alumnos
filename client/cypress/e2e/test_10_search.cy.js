// cypress/e2e/test_login.cy.js
// test search component
describe("Search Test", () => {
  it("Test search", () => {
    cy.delete_all_tournaments();
    cy.delete_all_players();
    // create 4 tournaments
    // const tournament_name = "tournament_%d_%d";
    cy.create_tournament_django(
      "LIC", // Lichess
      "SR", // Single Round Robin
      "tournament_name_" + 1 + "_" + 1
    );
    cy.create_tournament_django(
      "LIC", // Lichess
      "SR", // Single Round Robin
      "tournament_name_" + 1 + "_" + 2
    );
    cy.create_tournament_django(
      "LIC", // Lichess
      "SR", // Single Round Robin
      "tournament_name_" + 2 + "_" + 1
    );
    cy.create_tournament_django(
      "LIC", // Lichess
      "SR", // Single Round Robin
      "tournament_name_" + 2 + "_" + 2
    );
    cy.visit("/");
    // search for string '_1_'
    cy.get("[data-cy=input-search]").type("_1_");
    cy.get("[data-cy=submit-search]").click();
    // check that only tournaments with '_1_' are displayed
    cy.get('[data-cy="search-tournament_name_1_1"]').should("exist");
    cy.get('[data-cy="search-tournament_name_1_2"]').should("exist");
    cy.get('[data-cy="search-tournament_name_2_1"]').should("not.exist");
    cy.get('[data-cy="search-tournament_name_2_2"]').should("not.exist");
    cy.get('[data-cy="kk"]').should("not.exist");
  });
});
