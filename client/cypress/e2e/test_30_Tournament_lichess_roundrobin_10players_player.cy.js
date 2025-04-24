// cypress/e2e/test_play_scholar_check.js
// Create tournament, add players, add games, check ranking
// games are played in lichess
describe("Round Robing 10 players tournament Lichess", () => {
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
    ["zaragozana", "Philippe2020", "6wDHDmoG", b, 1, 3],
    ["Clavada", "oliva21", "FfxogVAC", w, 1, 4],
    ["rmarabini", "jpvalle", "55ig1Unu", w, 1, 5],

    ["jrcuesta", "jpvalle", "9utalUJp", w, 2, 1],
    ["oliva21", "rmarabini", "AR5pzMCh", b, 2, 2],
    ["Philippe2020", "Clavada", "rC3obSqS", b, 2, 3],
    ["eaffelix", "zaragozana", "Sh4NsnZL", w, 2, 4],
    ["ertopo", "soria49", "VrAvmsHj", w, 2, 5],

    ["soria49", "jrcuesta", "1ZqpLQNZ", b, 3, 1],
    ["zaragozana", "ertopo", "d4iJwwx6", w, 3, 2],
    ["Clavada", "eaffelix", "5c9O1o1n", b, 3, 3],
    ["rmarabini", "Philippe2020", "nCTZTPLJ", w, 3, 4],
    ["jpvalle", "oliva21", "8sNzS9Gd", w, 3, 5],

    ["jrcuesta", "oliva21", "zWQ9AkhW", w, 4, 1],
    ["Philippe2020", "jpvalle", "Mwz7JDfV", w, 4, 2],
    ["eaffelix", "rmarabini", "MixjLiYJ", w, 4, 3],
    ["ertopo", "Clavada", "imtdajQ7", w, 4, 4],
    ["soria49", "zaragozana", "FvfbbxVz", w, 4, 5],

    ["zaragozana", "jrcuesta", "ovdcpXi9", b, 5, 1],
    ["Clavada", "soria49", "lvBzqq6r", w, 5, 2],
    ["rmarabini", "ertopo", "HSZmXbAl", w, 5, 3],
    ["jpvalle", "eaffelix", "cGOSnA1m", b, 5, 4],
    ["oliva21", "Philippe2020", "7AMLRY6O", b, 5, 5],

    ["jrcuesta", "Philippe2020", "c6nEuUKV", b, 6, 1],
    ["eaffelix", "oliva21", "SqsAyCqy", w, 6, 2],
    ["ertopo", "jpvalle", "TLBzPZi1", d, 6, 3],
    ["soria49", "rmarabini", "oBJQXI1k", w, 6, 4],
    ["zaragozana", "Clavada", "Ayq4y0g9", b, 6, 5],

    ["Clavada", "jrcuesta", "ngssXIs2", w, 7, 1],
    ["rmarabini", "zaragozana", "fqjchXvi", d, 7, 2],
    ["jpvalle", "soria49", "7cmUKdFn", b, 7, 3],
    ["oliva21", "ertopo", "4dUXjjwz", b, 7, 4],
    ["Philippe2020", "eaffelix", "ztrkA9Z0", b, 7, 5],

    ["jrcuesta", "eaffelix", "vOOoBeE4", b, 8, 1],
    ["ertopo", "Philippe2020", "zkTJkfSN", b, 8, 2],
    ["soria49", "oliva21", "u3HmV0BJ", w, 8, 3],
    ["zaragozana", "jpvalle", "Wsr9W01S", b, 8, 4],
    ["Clavada", "rmarabini", "XT3URyTm", b, 8, 5],

    ["rmarabini", "jrcuesta", "TfRfymzv", w, 9, 1],
    ["jpvalle", "Clavada", "jk4IezIi", w, 9, 2],
    ["oliva21", "zaragozana", "TQDfnlrS", b, 9, 3],
    ["Philippe2020", "soria49", "FG72LOJK", b, 9, 4],
    ["eaffelix", "ertopo", "hHq30XSt", d, 9, 5],
  ];
  // row 1 lichess username
  // row 2 points
  // row 3 SB
  // row 4 black wins
  // row 5 wins
  const rankings = [
    ["eaffelix", "7.5", "5.00", "7.00"],
    ["rmarabini", "6.5", "4.00", "6.00"],
    ["soria49", "6", "4.00", "6.00"],
    ["Philippe2020", "5", "5.00", "5.00"],
    ["Clavada", "5", "4.00", "5.00"],
    ["ertopo", "5", "4.00", "4.00"],
    ["jrcuesta", "4", "5.00", "4.00"],
    ["jpvalle", "3.5", "5.00", "3.00"],
    ["zaragozana", "2.5", "4.00", "2.00"],
    ["oliva21", "0", "5.00", "0.00"],
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

  // rounds pairing should be as follows:
  // Round Robin table for 9 or 10 players:
  // 1 -> ertopo, etc
  // Rd 1: 1-10, 2-9, 3-8, 4-7, 5-6.
  // Rd 2: 10-6, 7-5, 8-4, 9-3, 1-2.
  // Rd 3: 2-10, 3-1, 4-9, 5-8, 6-7.
  // Rd 4: 10-7, 8-6, 9-5, 1-4, 2-3.
  // Rd 5: 3-10, 4-2, 5-1, 6-9, 7-8.
  // Rd 6: 10-8, 9-7, 1-6, 2-5, 3-4.
  // Rd 7: 4-10, 5-3, 6-2, 7-1, 8-9.
  // Rd 8: 10-9, 1-8, 2-7, 3-6, 4-5.
  // Rd 9: 5-10, 6-4, 7-3, 8-2, 9-1.

  it("round Robin Lichess tournament", () => {
    cy.delete_all_tournaments();
    cy.delete_all_players();
    const tournament_name = "tournament_SR";
    cy.create_tournament(
      "LIC", // Lichess
      "SR", // Single Round Robin
      tournament_name,
      headerLIC + playersLIC
    ); //add tournament name, different for each test.

    // Go to main page and...
    cy.visit("/");
    // cy.wait(2000)

    // ... select tournament
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
  });
});
