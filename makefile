export PGDATABASE := psi
export PGUSER := alumnodb
export PGPASSWORD := alumnodb
export PGCLIENTENCODING := LATIN9
export PGHOST := localhost
export DJANGOPORT := 8001
export DEBUG := True
# you must update the value of HEROKUHOST
export HEROKUHOST := git:remote protected-bastion-43256
PSQL = psql
CMD = python3 manage.py
HEROKU = heroku run export SQLITE=1 &
# Add applications to APP variable as they are
# added to settings.py file
APP = models 


# delete and create a new empty database
clear_db:
	@echo Clear Database
	dropdb --if-exists $(PGDATABASE)
	createdb

# create alumnodb super user
create_super_user:
	$(CMD) shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('alumnodb', 'admin@myproject.com', 'alumnodb')"

populate:
	@echo populate database
	python3 ./manage.py populate

runserver:
	$(CMD) runserver $(DJANGOPORT)

update_models:
	$(CMD) makemigrations $(APP)
	$(CMD) migrate

reset_db: clear_db update_models create_super_user

shell:
	@echo manage.py  shell
	@$(CMD) shell

dbshell:
	@echo manage.py dbshell
	@$(CMD) dbshell

addparticipants:
	@echo populate database
	python3 ./manage.py addparticipants



static:
	@echo manage.py collectstatic
	python3 ./manage.py collectstatic

fully_update_db:
	@echo del migrations and make migrations and migrate
	rm -rf */migrations
	python3 ./manage.py makemigrations $(APP) 
	python3 ./manage.py migrate

test_authentication:
	$(CMD) test models.test_authentication --keepdb

test_model:
	$(CMD) test models.test_models --keepdb

test_services:
	$(CMD) test create.test_services --keepdb

# other commands that may be useful but require tuning
#test_heroku:
#	$(HEROKU) $(CMD) test datamodel.tests_models.GameModelTests --keepdb & wait
#	$(HEROKU) $(CMD) test datamodel.tests_models.MoveModelTests --keepdb & wait
#	$(HEROKU) $(CMD) test datamodel.tests_models.my_tests --keepdb & wait
#
#test_query:
#	python3 test_query.py
#
#test_query_heroku:
#	$(HEROKU) python3 test_query.py
#
#config_heroku:
#	heroku login
#	heroku $HEROKUHOST
#
heroku_push:
	git push heroku master

heroku_bash:
	heroku run bash

heroku_dbshell:
	heroku pg:psql
