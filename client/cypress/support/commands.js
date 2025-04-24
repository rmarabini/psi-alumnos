// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })

// "export PYTHON3=/home/roberto/Docencia/PSI/psi/2023_24/psi2023_24/venv/bin/python\n" +
//
// fill free to modify the path to python3 and manage.py"

// Nothing to modify after this line
//==================================
// create test user, login, and verify log
// using the Forms

Cypress.Commands.add("logout", () => {
  cy.visit("/logout");
});

Cypress.Commands.add("login", (username, password) => {
  // login
  // const python = Cypress.env("python");
  // const manage = Cypress.env("manage");
  // cy.logout();
  cy.add_user("y", "y");
  // go tolog page
  cy.visit("/login");
  cy.wait(1000);
  // Fill in the login form
  // console.log("username", username)
  cy.get("[data-cy=username]").type(username);
  cy.get("[data-cy=password]").type(password);

  // Click the login button
  // we may have used
  // {enter} which causes the form to submit
  // cy.get('input[name=password]').type(`${password}{enter}`, { log: false })

  cy.get("[data-cy=login-button]").click();

  // we should be redirected to /login page
  cy.url().should("include", "/");
  cy.get('[data-cy="admin-log"]').contains(
    "Hello, you are logged in as an administrator"
  );
});

// delete tournament named tournament_name
// using django/python
Cypress.Commands.add("delete_tournament", (tournament_name) => {
  const python = Cypress.env("python");
  const manage = Cypress.env("manage");

  var command =
    "# delete tournament:" +
    tournament_name +
    "\n" +
    "export _PYTHON=" +
    python +
    "\n" +
    "export _MANAGE=" +
    manage +
    "\n" +
    "# nothing to modify before this line\n" +
    "\n" +
    "cat <<EOF | $_PYTHON $_MANAGE shell\n" +
    "from chess_models.models import Tournament\n" +
    "Tournament.objects.filter(name='" +
    tournament_name +
    "').delete()\n" +
    "EOF\n";
  cy.exec(command);
});

// delete all tournaments
// using django/python
Cypress.Commands.add("delete_all_tournaments", () => {
  const python = Cypress.env("python");
  const manage = Cypress.env("manage");

  var command =
    "# delete all tournaments" +
    "\n" +
    "export _PYTHON=" +
    python +
    "\n" +
    "export _MANAGE=" +
    manage +
    "\n" +
    "# nothing to modify before this line\n" +
    "\n" +
    "cat <<EOF | $_PYTHON $_MANAGE shell\n" +
    "from chess_models.models import Tournament\n" +
    "# reset secuences to 1\n" +
    "from django.db import connection\n" +
    "from django.apps import apps\n" +
    "\n" +
    "def reset_sequence(app_name, model_name):\n" +
    "    # Get the model class\n" +
    "    Model = apps.get_model(app_name, model_name)\n" +
    "    \n" +
    "    # Get the table name and the primary key column\n" +
    "    table_name = Model._meta.db_table\n" +
    "    primary_key_column = Model._meta.pk.column\n" +
    "    \n" +
    "    with connection.cursor() as cursor:\n" +
    "        # Get the name of the sequence associated with the primary key column\n" +
    "        cursor.execute(f\"SELECT pg_get_serial_sequence('{table_name}', '{primary_key_column}');\")\n" +
    "        sequence_name = cursor.fetchone()[0]\n" +
    "        \n" +
    "        if sequence_name:\n" +
    '            print(f"Resetting sequence {sequence_name} for {table_name}.{primary_key_column}")\n' +
    "            cursor.execute(f\"SELECT setval('{sequence_name}', 1, false) FROM {table_name};\")\n" +
    "        else:\n" +
    '            print(f"No sequence found for {table_name}.{primary_key_column}")\n' +
    "reset_sequence('chess_models', 'Tournament')\n" +
    "reset_sequence('chess_models', 'Player')\n" +
    "reset_sequence('chess_models', 'Game')\n" +
    "# FRST reset sequence then delete not the other way around\n" +
    "Tournament.objects.all().delete()\n" +
    "EOF\n";
  // cy.log("COMMAND: " + command);
  cy.exec(command);
});

// delete all players
// using django/python
Cypress.Commands.add("delete_all_players", () => {
  const python = Cypress.env("python");
  const manage = Cypress.env("manage");

  var command =
    "# delete all players" +
    "\n" +
    "export _PYTHON=" +
    python +
    "\n" +
    "export _MANAGE=" +
    manage +
    "\n" +
    "# nothing to modify before this line\n" +
    "\n" +
    "cat <<EOF | $_PYTHON $_MANAGE shell\n" +
    "from chess_models.models import Player\n" +
    "Player.objects.all().delete()\n" +
    "EOF\n";
  cy.exec(command);
});

// create tournament using django, No players
Cypress.Commands.add(
  "create_tournament_django",
  (
    tournament_board_type, //LIC
    tournament_type, //SR
    tournament_name
  ) => {
    const python = Cypress.env("python");
    const manage = Cypress.env("manage");

    var command =
      "# create tournament using django\n" +
      "export _PYTHON=" +
      python +
      "\n" +
      "export _MANAGE=" +
      manage +
      "\n" +
      "cat <<EOF | $_PYTHON $_MANAGE shell\n" +
      "from chess_models.models import Tournament\n" +
      "t = Tournament(name='" +
      tournament_name +
      "',\n" +
      "               board_type='" +
      tournament_board_type +
      "',\n" +
      "               tournament_type='" +
      tournament_type +
      "')\n" +
      "t.save()\n" +
      "EOF\n";
    cy.exec(command);
  }
);

// create tournament of type tournament type
// first delete the tournament
// then create the tournament
// and finally add players
// useing Forms
Cypress.Commands.add(
  "create_tournament",
  (
    tournament_board_type, //LIC
    tournament_type, //SR
    tournament_name,
    tournament_players
  ) => {
    //const tournament_name = 'tournament_test'
    // cy.delete_tournament(tournament_name)
    cy.login(Cypress.env("username"), Cypress.env("password"));
    cy.get("[data-cy=create-Tournament-button]").click();
    cy.init_ranking_system();
    // note that we can not use
    //     cy.visit('/createTournament')
    // because the store is lost
    //
    // delete tournament
    cy.get("[data-cy=name-cypress-test]")
      .scrollIntoView()
      .type(tournament_name);
    // uncheck only admin box
    cy.get("[data-cy=only_administrative-cypress-test]")
      .scrollIntoView()
      .uncheck();
    // select single robin
    cy.get("[data-cy=single_round_robin-cypress-test]")
      .scrollIntoView()
      .select(tournament_type);
    // boardtype lichess
    cy.get("[data-cy=boardtype-cypress-test]")
      .scrollIntoView()
      .select(tournament_board_type);
    // FormKit redefine this form
    // element and I do not know how to
    // use data-cy here so I am using the id
    // [id$=-option-sb] means that the id ends
    // with "-option-sb"
    //// Do not use sb since it is not implemented
    //// cy.get("[id$=-option-sb]").scrollIntoView().check({ force: true });
    cy.get("[id$=-option-wi]").scrollIntoView().check({ force: true });
    cy.get("[id$=-option-bt]").scrollIntoView().check({ force: true });
    // select tournament speed
    cy.get("[data-cy=tournament_speed-cypress-test]")
      .scrollIntoView()
      .select("CL");
    cy.get("[id=input_9]").scrollIntoView().type(tournament_players);

    // finally insert players
    // FormKit redefine this form
    // element and I do not know how to
    // use data-cy here so I am using the id
    // if (tournament_players == false) {
    //   if (tournament_board_type === "LIC") {
    //     cy.get("[id=input_9]")
    //       .scrollIntoView()
    //       .type("lichess_username\n")
    //       .type("ertopo\n")
    //       .type("soria49\n")
    //       .type("zaragozana\n")
    //       .type("Clavada\n")
    //       .type("rmarabini\n")
    //       .type("jpvalle\n")
    //       .type("oliva21\n")
    //       .type("Philippe2020\n")
    //       .type("eaffelix\n")
    //       .type("jrcuesta\n");
    //   }
    //   else {
    //     cy.get("[id=input_9]")
    //       .scrollIntoView()
    //       .type("name, email\n")
    //       .type("ertopo, ertopo@gmail.com\n")
    //       .type("soria49, soria49@gmail.com\n")
    //       .type("zaragozana, zaragozana@gmail.com\n")
    //       .type("Clavada, Clavada@gmail.com\n")
    //       .type("rmarabini, rmarabini@gmail.com\n")
    //       .type("jpvalle, jpvalle@gmail.com\n")
    //       .type("oliva21, oliva21@gmail.com\n")
    //       .type("Philippe2020, Philippe2020@gmail.com\n")
    //       .type("eaffelix, eaffelix@gmail.com\n")
    //       .type("jrcuesta, jrcuesta@gmail.com\n");
    //   }
    // }
    // else{
    //   cy.get("[id=input_9]")
    //     .scrollIntoView()
    //     .type(tournament_players);
    // }
    // click submit
    cy.get("form").submit(); // Submit a form
  }
);

// create user with username and password
// using django/python
Cypress.Commands.add("add_user", (username, password) => {
  const python = Cypress.env("python");
  const manage = Cypress.env("manage");

  var command =
    "# create user\n" +
    "export _PYTHON=" +
    python +
    "\n" +
    "export _MANAGE=" +
    manage +
    "\n" +
    "cat <<EOF | ${_PYTHON} ${_MANAGE} shell\n" +
    "from django.contrib.auth import get_user_model\n" +
    "User = get_user_model()\n" +
    "user, created = User.objects.get_or_create(" +
    "username='" +
    username +
    "');" +
    "user.set_password('" +
    password +
    "');" +
    "user.email = '" +
    username +
    "@gmail.com';" +
    "user.save()\n" +
    "EOF\n";
  // cy.log("COMMAND: " + command)
  cy.exec(command);
});

// create user with username and password
// using django/python
Cypress.Commands.add("create_player_django", (tournament_name, name, email) => {
  const python = Cypress.env("python");
  const manage = Cypress.env("manage");

  var command =
    "# create user\n" +
    "export _PYTHON=" +
    python +
    "\n" +
    "export _MANAGE=" +
    manage +
    "\n" +
    "cat <<EOF | ${_PYTHON} ${_MANAGE} shell\n" +
    "from django.contrib.auth import get_user_model\n" +
    "from chess_models.models import Player, Tournament\n" +
    "t = Tournament.objects.get(name=" +
    tournament_name +
    ")\n" +
    "player, created = Player.objects.get_or_create(" +
    "name='" +
    name +
    "');" +
    "lichess_username='" +
    name +
    "');" +
    "email = '" +
    email +
    "';" +
    "player.save()\n" +
    "t.players.add(player)\n" +
    "t.save()\n" +
    "EOF\n";
  // cy.log("COMMAND: " + command)
  cy.exec(command);
});

// // create user with username and password
// // using django/python
// Cypress.Commands.add("create_game_django", (tournament_name, white, black, result) => {
//   const python = Cypress.env("python");
//   const manage = Cypress.env("manage");

//   var command =
//     "# create user\n" +
//     "export _PYTHON=" + python + "\n" +
//     "export _MANAGE=" + manage + "\n" +
//     "cat <<EOF | ${_PYTHON} ${_MANAGE} shell\n" +
//     "from django.contrib.auth import get_user_model\n" +
//     "from chess_models.models import Player, Tournament\n" +
//     "t = Tournament.objects.get(name=" + tournament_name + ")\n" +
//     "p_white = Player.objects.get(name=" + white + ")\n" +
//     "p_black = Player.objects.get(name=" + black + ")\n" +
//     "game, created = Game.objects.get_or_create(" +
//     "white=p_white\n" +
//     "black=p_black\n" +
//     "lichess_username='" + name + "');" +
//     "email = '" + email + "';" +
//     "player.save()\n" +
//     "t.players.add(player)\n" +
//     "t.save()\n" +
//     "EOF\n";
//   // cy.log("COMMAND: " + command)
//   cy.exec(command);
// });

// populate model RankingSystemClass
// using django/python
Cypress.Commands.add("init_ranking_system", () => {
  const python = Cypress.env("python");
  const manage = Cypress.env("manage");

  var command =
    "# populate ranking class" +
    "\n" +
    "export _PYTHON=" +
    python +
    "\n" +
    "export _MANAGE=" +
    manage +
    "\n" +
    "# nothing to modify before this line\n" +
    "\n" +
    "cat <<EOF | ${_PYTHON} ${_MANAGE} shell\n" +
    "from chess_models.models import RankingSystemClass\n" +
    "from chess_models.models import RankingSystem\n" +
    "for ranking in RankingSystem:\n" +
    "    r, c = RankingSystemClass.objects.get_or_create(value=ranking)\n" +
    "r.save()\n" +
    "EOF\n";
  // cy.log("COMMAND: " + command)
  cy.exec(command);
});

// add results to a round for OTB games
Cypress.Commands.add("process_round", (round) => {
  round.forEach((tuple, index) => {
    let w = "w"; //'White wins (1-0)';
    let b = "b"; //'Black wins (0-1)';
    let d = "d"; //'Draw (1/2-1/2)';
    let result_to_input = { w: "1-0", b: "0-1", d: "½-½" };
    let result_to_select = {
      w: "White wins (1-0)",
      b: "Black wins (0-1)",
      d: "Draw (1/2-1/2)",
    };

    // get row from games table
    cy.log("tuple: " + tuple);
    const [white, black, gameID, result, roundN, gameN] = tuple; // Destructure the tuple

    // select input widget and select game result
    cy.get(`[data-cy=select-${roundN}-${gameN}]`)
      // Scroll the element into view
      .scrollIntoView({ offset: { top: -200, left: 0 } })
      .should("be.visible") // Ensure the element is visible
      .select(result_to_select[result], { force: true });

    // cypress does not handle javascript pop-ups
    // that is why we need to simulate a response
    // to the prompt widget BEFORE triggering it
    cy.window().then((win) => {
      // reset stub since it can not be reused inside a loop
      if (win.prompt.restore) {
        win.prompt.restore();
      }
      cy.log(white + "@example.com");
      cy.stub(win, "prompt").returns(white + "@example.com");
    });

    // click and send to server
    cy.get(`[data-cy=button-${roundN}-${gameN}]`)
      // Click the button, forcing the action if necessary
      .click({ force: true });
  }); // end forEach
});

Cypress.Commands.add("check_ranking", (ranking) => {
  // check ranking
  // select ranking piano
  cy.get("[data-cy=standing-accordion-button]")
    .scrollIntoView()
    .should("be.visible")
    .click({ force: true });

  ranking.forEach((tuple, index) => {
    const [name, points, sb, wins, black] = tuple; // Destructure the tuple
    cy.get(`[data-cy=ranking-${index + 1}]`)
      .scrollIntoView() // Scroll the element into view
      .should("be.visible") // Ensure the element is visible
      .should("contain.text", name)
      .should("contain.text", points)
      .should("contain.text", sb)
      .should("contain.text", black)
      .should("contain.text", wins);
  }); // end forEach
});
