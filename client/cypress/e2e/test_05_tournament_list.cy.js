// cypress/e2e/test_login.cy.js
// test touirnament list component including pagination
// npx cypress run  --spec  cypress/e2e/test_05_tournament_list.cy.js
describe("Tournament List Test", () => {
  it("Test tournament list", () => {
    cy.delete_all_tournaments();
    cy.delete_all_players();

    // create 5*5 tournaments
    const tournament_name = "tournament_name_";
    for (let i = 1; i <= 5; i++) {
      for (let j = 1; j <= 5; j++) {
        cy.create_tournament_django(
          "LIC", // Lichess
          "SR", // Single Round Robin
          tournament_name + i + "_" + j
        );
      }
    }

    cy.visit("/");
    cy.get("[data-cy=tournament_name_5_5]").should("exist");
    cy.get("[data-cy=tournament_name_1_1]").should("not.exist");
    // go to next page
    cy.get("[data-cy=next-button]").click();
    cy.get("[data-cy=tournament_name_5_5]").should("not.exist");
    cy.get("[data-cy=tournament_name_4_1]").should("exist");
    // go to next page
    cy.get("[data-cy=next-button]").click();
    cy.get("[data-cy=tournament_name_4_1]").should("not.exist");
    cy.get("[data-cy=tournament_name_3_1]").should("exist");
    // go to previous page
    cy.get("[data-cy=previous-button]").click();
    cy.get("[data-cy=tournament_name_4_1]").should("exist");
    cy.get("[data-cy=tournament_name_3_1]").should("not.exist");
  });
});

//   const header = "lichess_username\n";
//   const players =`ertopo
// jpvalle
// oliva21
// soria49
// zaragozana
// Philippe2020
// eaffelix
// Clavada
// rmarabini
// jrcuesta`;
