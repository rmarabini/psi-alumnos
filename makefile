export PGDATABASE := psi
export PGUSER := alumnodb
export PGPASSWORD := alumnodb
export PGCLIENTENCODING := LATIN9
export PGHOST := localhost
# you must update the value of HEROKUHOST
export HEROKUHOST := git:remote protected-bastion-43256
PSQL = psql
CMD = python3 manage.py
HEROKU = heroku run export SQLITE=1 &
# Add applications to APP variable as they are
# added to settings.py file
APP = catalog  orders

server:
	$(CMD) runserver

reset_db: clear_db update_db create_super_user

clear_db:
	@echo Clear Database
	dropdb --if-exists $(PGDATABASE)
	createdb

shell:
	@echo manage.py  shell
	@$(CMD) shell

dbshell:
	@echo manage.py dbshell
	@$(CMD) dbshell

populate:
	@echo populate database
	python3 ./manage.py populate

update_db:
	$(CMD) makemigrations $(APP)
	$(CMD) migrate

create_super_user:
	$(CMD) shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('alumnodb', 'admin@myproject.com', 'alumnodb')"

clear_update_db:
	@echo del migrations and make migrations and migrate
	rm -rf */migrations
	python3 ./manage.py makemigrations $(APP) 
	python3 ./manage.py migrate


test_catalog_datamodel:
	$(CMD) test catalog.tests_models

test_catalog_services:
	$(CMD) test catalog.tests_services

test_authentication_services:
	$(CMD) test authentication.tests_services

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
#push_heroku:
#	git push heroku master
