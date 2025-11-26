/// <reference types="cypress" />

context('Edit persona', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5173')
  })


  describe('Edit-persona', () => {
    it('Body and div', () => {
      cy.get('div#formulario-persona')
    })


    //Delete all elements 
    it('Delete all personas', () => {
      cy.get("table").find("tr").each(($el) => {
        $el.find('[data-cy=delete-button]').click()
      })

    })


    it('Add persona OK', () => {
      cy.get('[data-cy=name]').type("Paco1234")
      cy.get('[data-cy=surname]').type("Land")
      cy.get('[data-cy=email]').type("paco@land.com")
      cy.get('[data-cy=add-button]').click()
      cy.get('div.alert-success')
    })


    it('Edit persona + save', () => {

      cy.get("table").find("tr").its('length').then(intialLength => {

        cy.log('Initial len: ', intialLength)
        cy.get('table').contains('tr', 'Paco1234').find('[data-cy=edit-button]').click()
        cy.get('table').get('[data-cy=persona-nombre]').type("777")
        cy.get('table').get('[data-cy=save-button]').click()
        cy.get('table').contains('tr', 'Paco1234777')


        cy.get("table").find("tr").should("have.length", intialLength);

      })

    })

    it('Edit persona + cancel', () => {

      cy.get("table").find("tr").its('length').then(intialLength => {

        cy.log('Initial len: ', intialLength)
        cy.get('table').contains('tr', 'Paco1234').find('[data-cy=edit-button]').click()
        cy.get('table').get('[data-cy=persona-nombre]').type("777")
        cy.get('table').get('[data-cy=cancel-button]').click()
        cy.get('table').contains('tr', 'Paco1234')


        cy.get("table").find("tr").should("have.length", intialLength);

      })

    })
  })
})
