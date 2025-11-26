/// <reference types="cypress" />

context('Delete persona', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5173')
  })


  describe('Delete-persona', () => {
    it('Body and div', () => {
      cy.get('div#formulario-persona')
    })

    it('Add persona x 2 OK + Delete persona', () => {
      cy.get('[data-cy=name]').type("Paco")
      cy.get('[data-cy=surname]').type("Land")
      cy.get('[data-cy=email]').type("paco@land.com")
      cy.get('[data-cy=add-button]').click()
      cy.get('div.alert-success')

      cy.get('[data-cy=name]').type("Pepe")
      cy.get('[data-cy=surname]').type("Jean")
      cy.get('[data-cy=email]').type("pepe@jean.com")
      cy.get('[data-cy=add-button]').click()
      cy.get('div.alert-success')

      cy.get("table").find("tr").its('length').then(initialLength => {

        cy.log('Initial len', initialLength)
        cy.get('table').contains('tr', 'Paco').find('[data-cy=delete-button]').click()
        cy.get("table").find("tr").should("have.length", initialLength - 1);
      })

    })
  })
})
