// https://on.cypress.io/api

describe('Use the aplication', () => {
  it('visits the app root url', () => {
    
    // Go to root
    cy.visit('/', {timeout: 300000})
    // Go to login page
    // wait 5*60 sec so render can start
    cy.get('[data-cy="login-cypress-test"]').click();
    // type username and password
    cy.get('[data-cy="username"]', { timeout: 15000 })
      .should("be.visible")
      .type('alumnodb\n')
    cy.get('[data-cy="password"]', { timeout: 15000 })
      .should("be.visible")
      .type('alumnodb\n')
    // do not go to home with visit(/) because you reload the aplication
    // and token at lost, click in /home
    cy.get('[data-cy="home-cypress-test"]').click();
    cy.wait(5000);
   // cy.visit('/', {timeout: 10000})
    // check that random button exists
    cy.contains('Random song', { timeout: 15000 })
    // search for a song
    cy.get("[data-cy=search_text]", { timeout: 300000 })
      .scrollIntoView()
      .should("be.visible")
      .type('Here In The Real World')   
      
    cy.get('[data-cy="search_button"]')
      .click({ force: true });

    // check that the song is found
    cy.contains('Here In The Real World')
    // check that the song is playable
    cy.get('[data-cy="Here In The Real World"]')
      .should("be.visible")
      .click({ force: true });
      // play song
    //cy.wait(5000); // wait for the song to load
    // atart the audio
    cy.get('#my-audio', { timeout: 5000 }).then(($audio) => {
      $audio[0].play(); // Directly call play() on the DOM element
    });
    // Type first word: "heroes"
    cy.get('[data-cy="blankInput"]', { timeout: 15000 })
      .should("be.visible")
      .type('heroes\n')
    // skip second
    cy.get('[data-cy="skip"]', { timeout: 15000 })
      .should("be.visible")
      .click({ force: true })
    // wait and then type the third word: "love"
    cy.wait(5000); // wait for the song to play
    cy.get('[data-cy="blankInput"]', { timeout: 15000 })
      .should("be.visible")
      .type('love\n')
    // Type 4 word: "movies"
    cy.get('[data-cy="blankInput"]', { timeout: 15000 })
      .should("be.visible")
      .type('movies\n')
    // Type 5 word: "world"
    cy.get('[data-cy="blankInput"]', { timeout: 15000 })
      .should("be.visible")
      .type('kk\n')
      cy.wait(1000)
      cy.get('[data-cy="blankInput"]').clear();
      cy.get('[data-cy="blankInput"]', { timeout: 15000 })
      .should("be.visible")
      .type('pp\n')
      cy.wait(1000)
      cy.get('[data-cy="blankInput"]').clear();
      cy.get('[data-cy="blankInput"]', { timeout: 15000 })
      .should("be.visible")
      .type('world\n')
    // type 6 word: all
    cy.get('[data-cy="blankInput"]', { timeout: 15000 })
      .should("be.visible")
      .type('kk\n')
      cy.wait(1000)
      cy.get('[data-cy="blankInput"]').clear();
      cy.get('[data-cy="blankInput"]', { timeout: 15000 })
      .should("be.visible")
      .type('pp\n')
      cy.wait(1000)
      cy.get('[data-cy="blankInput"]').clear();
      cy.get('[data-cy="skip"]', { timeout: 15000 })
      .should("be.visible")
      .click({ force: true })
    // Type 7 word: "here"
      cy.get('[data-cy="blankInput"]', { timeout: 180000 })
      .should("be.visible")
      .type('here\n')
    // type 8 word: all
    cy.get('[data-cy="skip"]', { timeout: 25000 })
    .should("be.visible")
    .click({ force: true })
    // check correct answer
    cy.contains('Correct answers: 5 - Wrong answers: 7', { timeout: 60000 })
  })
})
