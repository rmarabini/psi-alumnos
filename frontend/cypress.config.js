const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    // append baseUrl to all URL used in the tests
    baseUrl: "http://localhost:5173",
    //specPattern: "cypress/e2e/**/*.{js,jsx,ts,tsx}",
  },
  // centralice some variables as username and password
  // use then in the test with "Cypress.env('username')"
  env: {
    username: "user1@example.com",
    username2: "user2@example.com",
    password: "sacacorchos"
  }
});
