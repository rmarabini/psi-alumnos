/// <reference types="cypress" />

context('Add persona', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5173')
  })
  
  
  describe('Add-persona', () => {
  it('Body and div', () => {
    cy.get('div#formulario-persona')
  })
  
   it('Add persona OK', () => {
    cy.get('[data-cy=name]').type("Paco")
    cy.get('[data-cy=surname]').type("Land")
    cy.get('[data-cy=email]').type("paco@land.com")
    cy.get('[data-cy=add-button]').click()    
    cy.get('div.alert-success')
  })
  
   it('Add persona KO 1', () => {
    cy.get('[data-cy=name]').type("Paco")
    cy.get('[data-cy=surname]').type("Land")
    cy.get('[data-cy=add-button]').click()    
    cy.get('div.alert-danger')
  })
    
   it('Add persona KO 2', () => {
    cy.get('[data-cy=name]').type("Paco")
    cy.get('[data-cy=email]').type("paco@land.com")
    cy.get('[data-cy=add-button]').click()    
    cy.get('div.alert-danger')
  })    

   it('Add persona KO 3', () => {
    cy.get('[data-cy=email]').type("paco@land.com")
    cy.get('[data-cy=add-button]').click()    
    cy.get('div.alert-danger')
  })  
   
   it('Add persona KO 4', () => {
    cy.get('[data-cy=add-button]').click()    
    cy.get('div.alert-danger')
  })     
  
   it('Add persona KO 5', () => {
    cy.get('[data-cy=name]').type("Paco")
    cy.get('[data-cy=surname]').type("Land")
    cy.get('[data-cy=email]').type("paco land.com")
    cy.get('[data-cy=add-button]').click()   
    cy.get('div.alert-danger').should("not.exist")
    cy.get('div.alert-success').should("not.exist")
  })  
    
   it('Add persona KO 6', () => {
    cy.get('[data-cy=name]').type("Paco")
    cy.get('[data-cy=surname]').type("Land")
    cy.get('[data-cy=email]').type("@land")
    cy.get('[data-cy=add-button]').click()   
    cy.get('div.alert-danger').should("not.exist")
    cy.get('div.alert-success').should("not.exist")
  })  
      
})

})
