describe('Initial website', () => {
  it('passes', () => {
    cy.visit('http://localhost:5173')
  })
})

describe('Formulario-persona', () => {
  it('Body and div', () => {
    cy.visit('http://localhost:5173')
    cy.get('body')
    cy.get('div#formulario-persona')
  })

  it('All components', () => {
    cy.visit('http://localhost:5173')
    cy.get('[data-cy=name]')
    cy.get('[data-cy=surname]')
    cy.get('[data-cy=email]')
    cy.get('[data-cy=add-button]')
  })

})

describe('Tabla persona', () => {
  it('Table', () => {
    cy.visit('http://localhost:5173')
    cy.get('body')
    cy.get('div#tabla-personas')
  })

  it('All components', () => {
    cy.visit('http://localhost:5173')
    cy.get('div#tabla-personas')
    if (cy.get('div#tabla-personas').children().not('[data-cy=no-persona]')) {
      cy.get('tr')
      cy.get('[data-cy=surname]')
      cy.get('[data-cy=email]')
    }
  })

})
