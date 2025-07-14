export DJANGOPORT := 8000
export DEBUG := True
export  PGHOST := localhost
export  PGDATABASE := song
export  PGUSER := alumnodb
export  PGPASSWORD := alumnodb
PSQL = psql
CMD = python manage.py
# Add applications to APP variable as they are
# added to settings.py file
APP = song_models 
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
	@$(CMD) collectstatic

update_db: clear_db
	@echo del migrations and make migrations and migrate
	rm -rf */migrations
	@$(CMD) makemigrations $(APP) 
	@$(CMD) migrate

populate:
	@$(CMD) populate
	
test_models:
	$(CMD) test song_models

test_api:
	$(CMD) test api

flake8:
	flake8 song_models
	flake8 api
conda:
	conda activate psi_2025
