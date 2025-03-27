const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    defaultCommandTimeout: 10000, // 10 seconds
    // append baseUrl to all URL used in the tests
    baseUrl: "http://localhost:5173",
    //specPattern: "cypress/e2e/**/*.{js,jsx,ts,tsx}",
  },
  // centralice some variables as username and password
  // use then in the test with "Cypress.env('username')"
  env: {
    username: "y",
    password: "y",
    python: "/home/roberto/miniconda/envs/chess/bin/python",
//    manage: "/home/roberto/Docencia/psi/2024-25/chesstournament/chesstournament_server/manage.py",
    manage: "/home/roberto/Docencia/PSI/psi/2024_25/chesstournament/chesstournament_server/manage.py",
  },
});
