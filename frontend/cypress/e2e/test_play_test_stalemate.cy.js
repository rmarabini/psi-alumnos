// cypress/e2e/test_play_scholar_check.js
// 
describe('Play a full game', () => {
    // you may need to modify this value
    const TEST_BOARD_SIZE_PX = 590;
    // nothing to change below this line

    // Define The moves of the game
    // this script will perform the odd (black) moves
    // the even (white) moves will be performed by the script
    // consumer_player_scholar_check.py
    const scholarCheckMoves = [
      ["a6", "a7"],
      ["b8", "a8"],
      ["b6", "a6"]
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
      scholarCheckMoves.forEach((tuple, index) => {
        //wait a few miliseconds
        cy.wait(1000)
        // check white move appears in table
        const [from, to] = tuple; // Destructure the tuple into to and from
        if (index % 2 === 0) {
          cy.log(`Counter: ${index}, Even`);
          cy.get('[data-cy=moveTable]' )
            .contains(from);
          cy.get('[data-cy=moveTable]' )
            .contains(to);
        }
        else {
          cy.log(`Counter: ${index}, Odd`);
          cy.getOffsetBySquare(TEST_BOARD_SIZE_PX, from, 'b').then(({ x, y }) => {
            cy.get('cg-board').click(x, y);});
          cy.getOffsetBySquare(TEST_BOARD_SIZE_PX, to, 'b').then(({ x, y }) => {
            cy.get('cg-board').click(x, y);});
            }
      });
      cy.get('[data-cy=winMsg]').contains('Stalemate');
      cy.wait(4000)
      cy.get('[data-cy=createGame-button-in-play]').contains('PLAY NEW GAME');
  })
})

  //cy.get('cg-board')
///      .trigger('mousedown', {button:1, x: 1+2*59.5, y: 1+2*59.5})
///      .trigger('mouseup',   {button:1, x: 1+2*59.5, y: 1+2*59.5})
