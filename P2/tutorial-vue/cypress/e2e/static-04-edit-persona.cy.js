/// <reference types="cypress" />

context('Edit persona', () => {
  beforeEach(() => {
    cy.visit('/')
  })


  describe('Edit-persona', () => {
    it('Body and div', () => {
      cy.get('div#formulario-persona')
    })


    it('Add persona OK + Edit persona + save', () => {
      cy.get('[data-cy=name]').type("Paco1234")
      cy.get('[data-cy=surname]').type("Land")
      cy.get('[data-cy=email]').type("pacoland@static3.com")
      cy.get('[data-cy=add-button]').click()
      cy.wait(2000)
      cy.get('div.alert-success')

      cy.get("table").find("tr").its('length').then(initialLength => {

        cy.log('Initial len: ', initialLength)
        cy.get('table').contains('tr', 'Paco1234').find('[data-cy=edit-button]').click()
        cy.get('table').get('[data-cy=persona-nombre]').type("777")
        cy.get('table').get('[data-cy=save-button]').click()
        cy.get('table').contains('tr', 'Paco1234777')

        cy.get("table").find("tr").should("have.length", initialLength);

      })
    })


    it('Add persona OK + Edit persona + cancel', () => {
      cy.get('[data-cy=name]').type("Paco1234")
      cy.get('[data-cy=surname]').type("Land")
      cy.get('[data-cy=email]').type("pacoland@static4.com")
      cy.get('[data-cy=add-button]').click()
      cy.wait(2000)
      cy.get('div.alert-success')

      cy.get("table").find("tr").its('length').then(initialLength => {

        cy.log('Initial len: ', initialLength)
        cy.get('table').contains('tr', 'Paco1234').find('[data-cy=edit-button]').click()
        cy.get('table').get('[data-cy=persona-nombre]').type("777")
        cy.get('table').get('[data-cy=cancel-button]').click()
        cy.wait(2000)
        cy.get('table').contains('tr', 'Paco1234')

        cy.get("table").find("tr").should("have.length", initialLength);
      })
    })
  })
})
