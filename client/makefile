# 
CMD = npm
# Add applications to APP variable as they are
# added to settings.py file
APP = models 

# run developement server
runserver:
	$(CMD) run dev


# install default modules for a new project
requirements:
	$(CMD) install bootstrap@5.3.0
	$(CMD) install @popperjs/core@2.11.5 
	$(CMD) install vue-router@4.1.5
	$(CMD) install vue3-chessboard@1.2.2

# install requirements for a given project
dependencies:
	$(CMD) -i 

init:
	npm init  vue@3.3.4

# ✔ Project name: … xxxxx
# ✔ Add TypeScript? … NO / Yes
# ✔ Add JSX Support? … No / Yes
# ✔ Add Vue Router for Single Page Application development? … No / YES
# ✔ Add Pinia for state management? … No / YES
# ✔ Add Vitest for Unit Testing? … No / YES
# ✔ Add Cypress for both Unit and End-to-End testing? … No / YES
# ✔ Add ESLint for code quality? … No / YES
# ✔ Add Prettier for code formatting? … No / YES

# Done. Now run:

#   cd vue-project
#   npm install
#   npm run lint
#   npm run dev
#     "allowJs": true,

