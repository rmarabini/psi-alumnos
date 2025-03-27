// cypress/e2e/test_create_tournament_admin.cy.js
// create different types types of tournaments
// and check games created
// ROB: test also the error message when
// trying to create two tournaments with the same name
// or with an invalid user

describe("Create Tournaments, several cases", () => {
  const headerLIC = "lichess_username\n";
  //  const headerOTB = "name, email\n";
  //  const playersOTB = `ertopo, ertopo@example.com
  //soria49, soria49@example.com
  //zaragozana, zaragozana@example.com
  //Clavada, Clavada@example.com
  //rmarabini, rmarabini@example.com
  //jpvalle, jpvalle@example.com
  //oliva21, oliva21@example.com
  //Philippe2020, Philippe2020@example.com
  //eaffelix, eaffelix@example.com
  //jrcuesta, jrcuesta@example.com
  //`;
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

  it("Create SR: Single Round Robin Tournament", () => {
    // Berger tables for 9-10 players
    // Rd 1: 1-10, 2-9, 3-8, 4-7, 5-6.
    // Rd 2: 10-6, 7-5, 8-4, 9-3, 1-2.
    // Rd 3: 2-10, 3-1, 4-9, 5-8, 6-7.
    // Rd 4: 10-7, 8-6, 9-5, 1-4, 2-3.
    // Rd 5: 3-10, 4-2, 5-1, 6-9, 7-8.
    // Rd 6: 10-8, 9-7, 1-6, 2-5, 3-4.
    // Rd 7: 4-10, 5-3, 6-2, 7-1, 8-9.
    // Rd 8: 10-9, 1-8, 2-7, 3-6, 4-5.
    // Rd 9: 5-10, 6-4, 7-3, 8-2, 9-1.
    cy.delete_all_tournaments();
    cy.delete_all_players();

    const tournament_name = "tournament_SR";
    cy.create_tournament(
      "LIC", // Lichess
      "SR", // Single Round Robin
      tournament_name,
      headerLIC + playersLIC
    ); //add tournament name, different for each test.

    cy.get("[data-cy=tournament-title]").contains(tournament_name);
    cy.get("[data-cy=round_1]").contains("round_001");
    cy.get("[data-cy=round_9]").contains("round_009");
    cy.get("[data-cy=round_10]").should("not.exist");
    cy.get("[data-cy=game_1_1]").contains("ertopo");
    cy.get("[data-cy=game_9_5]").contains("eaffelix");
    cy.get("[data-cy=game_9_6]").should("not.exist");
    cy.get("[data-cy=game_10_0]").should("not.exist");
  });

  it.skip("Create DR: Doble Round Robin Tournament", () => {
    // Berger table for double ronin
    // In this case, it is recommended,
    // the order of the last two rounds of each cycle should
    // be reversed. This is to avoid 3 consecutive games with
    // the same colour and does not work for a 4 player event
    // Berger tables for 9-10 players Doble robin
    // https://www.englishchess.org.uk/wp-content/uploads/2010/04/roundRobinPairings.pdf
    // Rd 1: 1-10, 2-9, 3-8, 4-7, 5-6.
    // Rd 2: 10-6, 7-5, 8-4, 9-3, 1-2.
    // Rd 3: 2-10, 3-1, 4-9, 5-8, 6-7.
    // Rd 4: 10-7, 8-6, 9-5, 1-4, 2-3.
    // Rd 5: 3-10, 4-2, 5-1, 6-9, 7-8.
    // Rd 6: 10-8, 9-7, 1-6, 2-5, 3-4.
    // Rd 7: 4-10, 5-3, 6-2, 7-1, 8-9.
    // Rd 8: 5-10, 6-4, 7-3, 8-2, 9-1.
    // Rd 9: 10-9, 1-8, 2-7, 3-6, 4-5.
    // Rd 10: 10-1, 9-2, 8-3, 7-4, 6-5.
    // Rd 11: 6-10, 5-7, 4-8, 3-9, 2-1.
    // Rd 12: 10-2, 1-3, 9-4, 8-5, 7-6.
    // Rd 13: 7-10, 6-8, 5-9, 4-1, 3-2.
    // Rd 14: 10-3, 2-4, 1-5, 9-6, 8-7.
    // Rd 15: 8-10, 7-9, 6-1, 5-2, 4-3.
    // Rd 16: 10-4, 3-5, 2-6, 1-7, 9-8.
    // Rd 17: 10-5, 4-6, 3-7, 2-8, 1-9.
    // Rd 18: 9-10, 8-1, 7-2, 6-3, 5-4.

    cy.delete_all_tournaments();
    cy.delete_all_players();
    const tournament_name = "tournament_DR";
    cy.create_tournament("LIC", "DR", tournament_name, headerLIC + playersLIC); //add tournament name, different for each test.
    cy.get("[data-cy=tournament-title]").contains(tournament_name);
    cy.get("[data-cy=round_1]").contains("round_001");
    cy.get("[data-cy=round_18]").contains("round_018");
    cy.get("[data-cy=round_19]").should("not.exist");
    cy.get("[data-cy=game_1_1]").contains("ertopo");
    cy.get("[data-cy=game_9_1]").contains("jrcuesta");
    cy.get("[data-cy=game_9_6]").should("not.exist");
    cy.get("[data-cy=game_10_1]").contains("jrcuesta");
    cy.get("[data-cy=game_18_1]").contains("eaffelix");
  });

  it.skip("Create DD: Doble Round Robin same day Tournament", () => {
    // Berger tables for 9-10 players double robin same day
    // Rd 1: 1-10, 2-9, 3-8, 4-7, 5-6.
    // Rd 2: 10-1, 9-2, 8-3, 7-4, 6-5.
    // Rd 3: 10-6, 7-5, 8-4, 9-3, 1-2.
    // Rd 4: 6-10, 5-7, 4-8, 3-9, 2-1.
    // Rd 5: 2-10, 3-1, 4-9, 5-8, 6-7.
    // Rd 6: 10-2, 1-3, 9-4, 8-5, 7-6.
    // Rd 7: 10-7, 8-6, 9-5, 1-4, 2-3.
    // Rd 8: 7-10, 6-8, 5-9, 4-1, 3-2.
    // Rd 9: 3-10, 4-2, 5-1, 6-9, 7-8.
    // Rd 10: 10-3, 2-4, 1-5, 9-6, 8-7.
    // Rd 11: 10-8, 9-7, 1-6, 2-5, 3-4.
    // Rd 12: 8-10, 7-9, 6-1, 5-2, 4-3.
    // Rd 13: 4-10, 5-3, 6-2, 7-1, 8-9.
    // Rd 14: 10-4, 3-5, 2-6, 1-7, 9-8.
    // Rd 15: 10-9, 1-8, 2-7, 3-6, 4-5.
    // Rd 16: 9-10, 8-1, 7-2, 6-3, 5-4.
    // Rd 17: 5-10, 6-4, 7-3, 8-2, 9-1.
    // Rd 18: 10-5, 4-6, 3-7, 2-8, 1-9.

    cy.delete_all_tournaments();
    cy.delete_all_players();
    const tournament_name = "tournament_DD";
    cy.create_tournament("LIC", "DD", tournament_name, headerLIC + playersLIC); //add tournament name, different for each test.
    cy.get("[data-cy=tournament-title]").contains(tournament_name);
    cy.get("[data-cy=round_1]").contains("round_001");
    cy.get("[data-cy=round_18]").contains("round_018");
    cy.get("[data-cy=round_19]").should("not.exist");
    cy.get("[data-cy=game_1_1]").contains("ertopo");
    cy.get("[data-cy=game_1_2]").contains("soria49");
    cy.get("[data-cy=game_2_1]").contains("jrcuesta");
    cy.get("[data-cy=game_2_2]").contains("eaffelix");
    cy.get("[data-cy=game_9_1]").contains("zaragozana");
    cy.get("[data-cy=game_9_6]").should("not.exist");
    cy.get("[data-cy=game_10_1]").contains("jrcuesta");
    cy.get("[data-cy=game_18_1]").contains("jrcuesta");
  });

  it.skip("Create SW: Swiss Tournament", () => {
    cy.delete_all_tournaments();
    cy.delete_all_players();
    const tournament_name = "tournament_SW";
    cy.create_tournament("LIC", "SW", tournament_name, headerLIC + playersLIC); //add tournament name, different for each test.
    cy.get("[data-cy=tournament-title]").contains(tournament_name);
    cy.get("[data-cy=round_1]").contains("round_001");
    cy.get("[data-cy=round_2]").should("not.exist");
    cy.get("[data-cy=game_1_1]").contains("ertopo");
    cy.get("[data-cy=game_1_2]").contains("oliva21");
    cy.get("[data-cy=game_1_3]").contains("zaragozana");
    cy.get("[data-cy=game_1_4]").contains("eaffelix");
    cy.get("[data-cy=game_1_5]").contains("rmarabini");
    cy.get("[data-cy=game_2_1]").should("not.exist");
  });

  it("Create Two tornaments with the same name (try to)", () => {
    cy.delete_all_tournaments();
    cy.delete_all_players();

    const tournament_name = "tournament_SR";
    cy.create_tournament(
      "LIC", // Lichess
      "SR", // Single Round Robin
      tournament_name,
      headerLIC + playersLIC
    ); //add tournament name, different for each test.
    cy.get("[data-cy=error-message]").should("not.exist");
    cy.create_tournament(
      "LIC", // Lichess
      "SR", // Single Round Robin
      tournament_name,
      headerLIC + playersLIC
    ); //add tournament name, different for each test.

    // cy.get('[data-cy=error-message]').contains('Error: Tournament name already exists');
  });

  it("Create a turnament with an invalid user", () => {
    cy.delete_all_tournaments();
    cy.delete_all_players();

    const tournament_name = "tournament_SR";
    const tournament_players = `lichess_username
ertopo
soria49
zaragozana
qhlw9027xn++++**ax34vgr`;
    cy.create_tournament(
      "LIC", // Lichess
      "SR", // Single Round Robin
      tournament_name, //add tournament name, different for each test.
      tournament_players
    );

    cy.get("[data-cy=error-message]").contains(
      "Error: can not add players to tournament"
    );
  });
});
