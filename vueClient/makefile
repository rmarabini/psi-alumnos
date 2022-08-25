# 
CMD = npm
# Add applications to APP variable as they are
# added to settings.py file
APP = models 

# run developement server
runserver:
	$(CMD) run dev


# install defetault module for a new project
requirements:
	$(CMD) install bootstrap@5.1.3
	$(CMD) install @popperjs/core@2.11.5
	$(CMD) install axios@0.27.2 
	$(CMD) install vuex@4.0.2

# install requirements for a given project
dependencies:
	$(CMD) -i 

init:
	npm init  vue@3.2

lint:
	npm run lint

# ✔ Project name: … vue-project
# ✔ Add TypeScript? … *No* / Yes
# ✔ Add JSX Support? … *No* / Yes
# ✔ Add Vue Router for Single Page Application development? … No / *Yes*
# ✔ Add Pinia for state management? … *No* / Yes
# ✔ Add Vitest for Unit Testing? … *No* / Yes
# ✔ Add Cypress for both Unit and End-to-End testing? … *No* / Yes
# ✔ Add ESLint for code quality? … No / *Yes*
# ✔ Add Prettier for code formatting? … No / *Yes*

# Done. Now run:

#   cd vue-project
#   npm install
#   npm run lint
#   npm run dev
#     "allowJs": true,

