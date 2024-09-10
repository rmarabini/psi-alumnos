export DJANGOPORT := 8000
export DEBUG := True
export  PGHOST := localhost
export  PGDATABASE := chess
export  PGUSER := alumnodb
export  PGPASSWORD := alumnodb
PSQL = psql
CMD = python manage.py
# Add applications to APP variable as they are
# added to settings.py file
APP = chess_models 
export DATABASE_URL = postgres://alumnodb:alumnodb@localhost/$(PGDATABASE)

## delete and create a new empty database
clear_db:
	@echo Clear Database
	dropdb --if-exists $(PGDATABASE)
	createdb

# create alumnodb super user
create_super_user:
	$(CMD) shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('alumnodb', 'admin@myproject.com', 'alumnodb')"

runserver:
	$(CMD) runserver $(DJANGOPORT)

update_models:
	$(CMD) makemigrations $(APP)
	$(CMD) migrate

shell:
	@echo manage.py  shell
	@$(CMD) shell

dbshell:
	@echo manage.py dbshell
	@$(CMD) dbshell

static:
	@echo manage.py collectstatic
	python3 ./manage.py collectstatic

force_update_db: clear_db
	@echo del migrations and make migrations and migrate
	rm -rf */migrations
	python3 ./manage.py makemigrations $(APP) 
	python3 ./manage.py migrate

populate:
	python3 ./manage.py populate
	
cypress_test_01_lichess: force_update_db
	@echo delete and create database $(PGDATABASE)
	@echo execute populates
	@$(CMD) populate_tournament_game_lichess
	
cypress_test_01_otb: force_update_db
	@echo delete and create database $(PGDATABASE)
	@echo execute populates
	@$(CMD) populate_tournament_game_otb

test_chess_models:
	$(CMD) test chess_models.tests	

test_api:
	$(CMD) test api.test_api

conda:
	conda activate chess
