// cypress/e2e/test_game.cy.js
describe('Login Test', () => {
    it('LogIn and select game option "Join Any Game"', () => {
      cy.login(Cypress.env('username'), Cypress.env('password'))

      //We are in the /creategame.
      // Get the dropdown element by its ID
      cy.get('#selectGame').select("game_join_any")
      cy.get('#selectGame').select("game_join_any").should("have.value", "game_join_any")

      // Verify that the selected option is now the active one
      cy.get("select option:selected")
        .invoke("text")
        .should("eq", "Join any game")
      
      // Check that there is no place to type gameID
      cy.get('[data-cy="gameID"]').should('not.exist')  
   });
   // it.only('only run this one', () => {
   // similarly use it.skip(...) to skip a test
   it('LogIn and select game option "Join specific Game"', () => {
    cy.login(Cypress.env('username'), Cypress.env('password'))

    //We are in the /creategame.
    // Get the dropdown element by its ID
    cy.get('#selectGame').select("Join specific game (gameID required)")

    // Verify that the selected option is now the active one
    cy.get("select option:selected")
      .invoke("text")
      .should("eq", "Join specific game (gameID required)")

    // check that there is a place to type the game ID
    cy.get('[data-cy="gameID"]').contains('Enter gameID')  
    });

    // try to create a game before login
    // This test may fail if the vue page 
    // that creates the game is protected
    // againts anonymous users
    it('Try to create a game before login', () => {
      // cy.exec("./create_user.sh");
      cy.visit("/creategame"); //go to open game
      cy.get('#selectGame').select("Join any game")
      cy.get('[data-cy=createGame-button]').click();
      cy.get('[data-cy=error-message]').contains('Error: Cannot create game');

    });

    // create game after login in
    it('Try to create a game after login', () => {
      cy.login(Cypress.env('username'), Cypress.env('password'))
      cy.get('#selectGame').select("Join any game")
      cy.get('[data-cy=createGame-button]').click();
    
      // check something so the play page appears...
      cy.url().should('include', 'http');
    });

  })