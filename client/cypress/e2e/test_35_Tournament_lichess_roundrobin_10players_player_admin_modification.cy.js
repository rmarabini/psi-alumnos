// cypress/e2e/test_play_scholar_check.js
// Create tournament, add players, add games, check ranking
// games are played in lichess
// admin user modifies some results
describe("Round Robing 10 players tournament Lichess, admin modify results", () => {
  // nothing to change below this line

  // follow alist with the games
  // the first element is the white player
  // the second element is the black player
  // the third element is the lichess game ID
  // the fourth element is the result
  // the fifth element is the round
  // the sixth element is the game number (not id)
  let w = "1-0";
  let b = "0-1";
  let d = "½-½";
  const games = [
    ["ertopo", "jrcuesta", "tfjv7FIV", w, 1, 1],
    ["soria49", "eaffelix", "1e3OdSDN", w, 1, 2],
  ];
  // row 1 lichess username
  // row 2 points
  // row 3 no wins
  // row 4 play as black
  // ranking before modification by admin user
  const rankings = [
    ["ertopo", "1", "1.00", "0.00"],
    ["soria49", "1", "1.00", "0.00"],
    ["eaffelix", "0", "0.00", "1.00"],
    ["jrcuesta", "0", "0.00", "1.00"],
    ["zaragozana", "0", "0.00", "0.00"],
    ["Clavada", "0", "0.00", "0.00"],
    ["rmarabini", "0", "0.00", "0.00"],
    ["jpvalle", "0", "0.00", "0.00"],
    ["oliva21", "0", "0.00", "0.00"],
    ["Philippe2020", "0", "0.00", "0.00"],
  ];
  // ranking after modification by admin user
  const rankings2 = [
    ["jrcuesta", "1", "1.00", "1.00"],
    ["soria49", "1", "1.00", "0.00"],
    ["eaffelix", "0", "0.00", "1.00"],
    ["ertopo", "0", "0.00", "0.00"],
    ["zaragozana", "0", "0.00", "0.00"],
    ["Clavada", "0", "0.00", "0.00"],
    ["rmarabini", "0", "0.00", "0.00"],
    ["jpvalle", "0", "0.00", "0.00"],
    ["oliva21", "0", "0.00", "0.00"],
    ["Philippe2020", "0", "0.00", "0.00"],
  ];
  const headerLIC = "lichess_username\n";
  const headerOTB = "name, email\n";
  const playersOTB = `ertopo, ertopo@example.com
soria49, soria49@example.com
zaragozana, zaragozana@example.com
Clavada, Clavada@example.com
rmarabini, rmarabini@example.com
jpvalle, jpvalle@example.com
oliva21, oliva21@example.com
Philippe2020, Philippe2020@example.com
eaffelix, eaffelix@example.com
jrcuesta, jrcuesta@example.com
`;
  const playersLIC = `ertopo
soria49
zaragozana
Clavada
rmarabini
jpvalle
oliva21
Philippe2020
eaffelix
jrcuesta
`;

  it("round Robin Lichess tournament, admin modifies results", () => {
    cy.delete_all_tournaments();
    cy.delete_all_players();
    const tournament_name = "tournament_SR";
    cy.create_tournament(
      "LIC", // Lichess
      "SR", // Single Round Robin
      tournament_name,
      headerLIC + playersLIC
    ); //add tournament name, different for each test.
    // Go to main page
    cy.visit("/");

    // select tournament
    cy.get("[data-cy=" + tournament_name + "]").click();

    // Now we are in the games page
    games.forEach((tuple, index) => {
      // get row from games table
      const [white, black, gameID, result, roundN, gameN] = tuple; // Destructure the tuple
      // select input widget and type game ID
      cy.get(`[data-cy=input-${roundN}-${gameN}]`)
        .scrollIntoView({ offset: { top: -150, left: 0 } }) // Scroll the element into view
        .should("be.visible") // Ensure the element is visible
        .clear({ force: true }) // Clear the input field, forcing the action if necessary
        .type(gameID, { force: true }); // Type into the input field, forcing the action if necessary
      // click
      // cy.wait(500)
      cy.get(`[data-cy=button-${roundN}-${gameN}]`)
        //.scrollIntoView( {offset: { top: -50, left: 0 }})           // Scroll the element into view
        //.should('be.visible')       // Ensure the element is visible
        .click({ force: true }); // Click the button, forcing the action if necessary
      // check results
      cy.get(`[data-cy=input-${roundN}-${gameN}]`).should(
        "contain.text",
        `${result}`
      );
    }); // end forEach
    // check extra column does NOT exist
    cy.get('[data-cy="select-admin-1-1"]').should("not.exist");
    // check results
    // select ranking piano
    cy.get("[data-cy=standing-accordion-button]")
      .scrollIntoView()
      .should("be.visible")
      .click({ force: true });
    // check ranking
    rankings.forEach((tuple, index) => {
      const [name, points, black, wins] = tuple; // Destructure the tuple
      cy.get(`[data-cy=ranking-${index + 1}]`)
        .scrollIntoView() // Scroll the element into view
        .should("be.visible") // Ensure the element is visible
        .should("contain.text", name)
        .should("contain.text", points)
        .should("contain.text", black)
        .should("contain.text", wins);
    }); // end forEach

    // login
    cy.visit("/"); // login is lost at this point
    cy.login(Cypress.env("username"), Cypress.env("password"));
    // select tournament
    cy.get("[data-cy=tournament_SR]").click();
    // check extra column
    cy.get("[data-cy=select-admin-1-1]").should("exist");
    // modify reults
    // select input widget and select game result
    cy.get(`[data-cy=select-admin-1-1]`)
      // Scroll the element into view
      .scrollIntoView({ offset: { top: -200, left: 0 } })
      .should("be.visible") // Ensure the element is visible
      .select("Black wins (0-1)", { force: true });
    // click
    // cy.wait(500)
    cy.get(`[data-cy=button-admin-1-1]`).click({ force: true });

    // check we have selected the right result
    cy.get(`[data-cy=input-1-1]`).should("contain.text", "0-1");

    // check modification
    // select ranking piano
    cy.get("[data-cy=standing-accordion-button]")
      .scrollIntoView()
      .should("be.visible")
      .click({ force: true });
    // check ranking after modification
    rankings2.forEach((tuple, index) => {
      const [name, points, black, wins] = tuple; // Destructure the tuple
      cy.get(`[data-cy=ranking-${index + 1}]`)
        .scrollIntoView() // Scroll the element into view
        .should("be.visible") // Ensure the element is visible
        .should("contain.text", name)
        .should("contain.text", points)
        .should("contain.text", black)
        .should("contain.text", wins);
    }); // end forEach
  });
});
