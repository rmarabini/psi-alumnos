export DJANGOPORT := 8001
export DEBUG := True
PSQL = psql
CMD = python3 manage.py
# Add applications to APP variable as they are
# added to settings.py file
APP = models 
# update neon database
export DATABASE_URL = postgres://qgdzyaxe:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@lucky.db.elephantsql.com/qgdzyaxe

## delete and create a new empty database
#clear_db:
#	@echo Clear Database
#	dropdb --if-exists $(PGDATABASE)
#	createdb

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

fully_update_db:
	@echo del migrations and make migrations and migrate
	rm -rf */migrations
	python3 ./manage.py makemigrations $(APP) 
	python3 ./manage.py migrate

test_model:
	$(CMD) test models.test_models --keepdb

