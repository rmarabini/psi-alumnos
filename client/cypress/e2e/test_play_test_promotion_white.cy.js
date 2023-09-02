// cypress/e2e/test_play_scholar_check.js
// 
describe('Play a full game', () => {
    // you may need to modify this value
    const TEST_BOARD_SIZE_PX = 592;
    // nothing to change below this line

    // Define The moves of the game
    // this script will perform the odd (black) moves
    // the even (white) moves will be performed by the script
    // consumer_player_scholar_check.py
    const moves = [
      ["e2", "e4", ""],
      ["e7", "e5", ""],
      ["f2", "f4", ""],
      ["e5", "f4", ""],
      ["g2", "g3", ""],
      ["f4", "g3", ""],
      ["d1", "e2", ""],
      ["g3", "h2", ""],
      ["e2", "g4", ""],
      ["h2", "g1", "q"],
      ["a2", "a3", ""],
      ["g1", "h2", ""],
    ];
    it('LogIn and play (scholar check)', () => {
      // login using user2 (black)
      // players created by python script
      cy.login(Cypress.env('username2'), Cypress.env('password'))
      // join game
      cy.get('#selectGame').select("Join any game")
      cy.get('[data-cy=createGame-button]').click();
    
      // we are in the page to play
      moves.forEach((tuple, index) => {
        //wait a few miliseconds
        cy.wait(200)
        // check white move appears in table
        const [from, to] = tuple; // Destructure the tuple into to and from
        if (index % 2 === 1) {
          cy.log(`Counter: ${index}, Odd`);
        }
        else {
          cy.log(`Counter: ${index}, Even`);
          cy.getOffsetBySquare(TEST_BOARD_SIZE_PX, from, 'w').then(({ x, y }) => {
            cy.get('cg-board').click(x, y);});
          cy.getOffsetBySquare(TEST_BOARD_SIZE_PX, to, 'w').then(({ x, y }) => {
            cy.get('cg-board').click(x, y);});
            }
        //if (index===9){
        //  //choose queen promotion
        //  const QUEENPROMOTIONSQUARE = 44
        //  cy.get('[class*="queen white"]').click(QUEENPROMOTIONSQUARE, QUEENPROMOTIONSQUARE, {force: true});
        //}
        cy.get('[data-cy=moveTable]' )
          .contains(from);
        cy.get('[data-cy=moveTable]' )
          .contains(to);
          });
  })
})

  //cy.get('cg-board')
///      .trigger('mousedown', {button:1, x: 1+2*59.5, y: 1+2*59.5})
///      .trigger('mouseup',   {button:1, x: 1+2*59.5, y: 1+2*59.5})
