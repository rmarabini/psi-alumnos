/// <reference types="cypress" />

context('Delete persona', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5173')
  })


  describe('Delete-persona', () => {
    it('Body and div', () => {
      cy.get('div#formulario-persona')
    })

    it('Add persona OK', () => {
      cy.get('[data-cy=name]').type("Paco_delete")
      cy.get('[data-cy=surname]').type("Land")
      cy.get('[data-cy=email]').type("paco@land.com")
      cy.get('[data-cy=add-button]').click()
      cy.get('div.alert-success')
    })


    it('Delete persona', () => {

      cy.get("table").find("tr").its('length').then(intialLength => {

        cy.log('Initial len', intialLength)
        // Code that uses initialLength is nested inside `.then()`

        cy.get('table').contains('tr', 'Paco_delete').find('[data-cy=delete-button]').click()
        cy.get("table").find("tr").should("have.length", intialLength - 1);

      })

    })
  })
})
