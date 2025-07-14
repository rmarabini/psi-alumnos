// cypress/e2e/test_play_scholar_check.js
// 
describe('Play a full game', () => {
    // you may need to modify this value
    const TEST_BOARD_SIZE_PX = Cypress.env('TEST_BOARD_SIZE_PX');
    // nothing to change below this line

    // Define The moves of the game
    // this script will perform the odd (black) moves
    // the even (white) moves will be performed by the script
    // consumer_player_scholar_check.py
    const moves =[
      ["e2", "e4", ""],
      ["e7", "e5", ""],
      ["g1", "f3", ""],
      ["b8", "c6", ""],
      ["f1", "b5", ""],
      ["a7", "a6", ""],
      ["b5", "a4", ""],
      ["b7", "b5", ""],
      ["a4", "b3", ""],
      ["f8", "c5", ""],
      ["e1", "g1", ""],
      ["g8", "f6", ""],
      ["d2", "d3", ""],
      ["e8", "g8", ""],
      ["b1", "c3", ""],
      ["d7", "d6", ""],
      ["c3", "e2", ""],
      ["h7", "h6", ""],
      ["e2", "g3", ""],
      ["c6", "d4", ""],
      ["f3", "d4", ""],
      ["c5", "d4", ""],
      ["c2", "c3", ""],
      ["d4", "b6", ""],
      ["d1", "f3", ""],
      ["c8", "g4", ""],
      ["f3", "f5", ""],
      ["g4", "f5", ""],
      ["g3", "f5", ""],
      ["f6", "g4", ""],
      ["h2", "h3", ""],
      ["b6", "f2", ""],
      ["f1", "f2", ""],
      ["g4", "f2", ""],
      ["g1", "f2", ""],
      ["d8", "f6", ""],
      ["g2", "g4", ""],
      ["g7", "g6", ""],
      ["c1", "h6", ""],
      ["g6", "f5", ""],
      ["h6", "f8", ""],
      ["f5", "g4", ""],
      ["f2", "e3", ""],
      ["f6", "f3", ""],
      ["e3", "d2", ""],
      ["f3", "f2", ""],
      ["d2", "c1", ""],
      ["a8", "f8", ""],
      ["a2", "a4", ""],
      ["f2", "f1", ""],
      ["b3", "d1", ""],
      ["f1", "d3", ""],
      ["a4", "b5", ""],
      ["a6", "b5", ""],
      ["d1", "g4", ""],
      ["d3", "e4", ""],
      ["c1", "d2", ""],
      ["e4", "f4", ""],
      ["d2", "c2", ""],
      ["f4", "h2", ""],
      ["c2", "b3", ""],
      ["f7", "f5", ""],
      ["a1", "f1", ""],
      ["f5", "g4", ""],
      ["f1", "f8", ""],
      ["g8", "f8", ""],
      ["h3", "g4", ""],
      ["h2", "f4", ""],
      ["g4", "g5", ""],
      ["f4", "g5", ""],
      ["c3", "c4", ""],
      ["b5", "c4", ""],
      ["b3", "c4", ""],
      ["f8", "e7", ""],
      ["c4", "d5", ""],
      ["g5", "d2", ""],
      ["d5", "c6", ""],
      ["d2", "c2", ""],
      ["c6", "d5", ""],
      ["e7", "d7", ""],
      ["b2", "b4", ""],
      ["e5", "e4", ""],
      ["d5", "d4", ""],
      ["c2", "d3", ""],
    ];

    it('LogIn and play (scholar check)', () => {
      // login using user2 (black)
      // players created by python script
      cy.login(Cypress.env('username2'), Cypress.env('password'))
      // join game
      cy.get('#selectGame').select("Join any game")
      cy.get('[data-cy=createGame-button]').click();
    
      // we are in the page to play
      //cy.url().should('include', 'http');
      moves.forEach((tuple, index) => {
        //wait a few miliseconds
        cy.wait(200)
        // check white move appears in table
        const [from, to] = tuple; // Destructure the tuple into to and from
        if (index % 2 === 0) {
          cy.log(`Counter: ${index}, Even`);
          cy.get('[data-cy=moveTable]' , { timeout: 20000 })
            .contains(from);
          cy.get('[data-cy=moveTable]' , { timeout: 20000 })
            .contains(to);
        }
        else {
          cy.log(`Counter: ${index}, Odd`);
          cy.getOffsetBySquare(TEST_BOARD_SIZE_PX, from, 'b').then(({ x, y }) => {
            cy.get('cg-board', { timeout: 10000 }).click(x, y);});
          cy.getOffsetBySquare(TEST_BOARD_SIZE_PX, to, 'b').then(({ x, y }) => {
            cy.get('cg-board', { timeout: 10000 }).click(x, y);});
            }
      });
      cy.get('[data-cy=winMsg]').contains('Black Wins');
      cy.wait(4000)
      cy.get('[data-cy=createGame-button-in-play]').contains('PLAY NEW GAME');
  })
})

  //cy.get('cg-board')
///      .trigger('mousedown', {button:1, x: 1+2*59.5, y: 1+2*59.5})
///      .trigger('mouseup',   {button:1, x: 1+2*59.5, y: 1+2*59.5})
