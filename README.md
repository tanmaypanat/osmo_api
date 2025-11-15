# osmo_api
Repository for osmo take home assignment 

## Setup instructions
- Install docker 
    - This is a simple docker install for ubuntu 24, do this is docker is not already installed
    - sudo apt update
    - sudo apt install docker.io
    - sudo usermod -aG docker ${USER}
    - log out then log in session
    - docker run hello-world

- clone repo
    - git clone https://github.com/tanmaypanat/osmo_api.git

- create python virtual enviroment 
    - python3 -m venv osmoenv
    - source osmoenv/bin/activate

- cd osmo_api ( this is the cloned directory)

- pip install -r requirements.txt // to install requirements inside env
- pip list  // to confirm

- docker compose up -d or docker-compose up -d  // depending on docker version 
- docker ps // confirms container is up and running 

- server will run on localhost:8080, make sure no other process has that.

## Testing instructions 
- in the activated python env run this command to start server 
    - python3 -m app.main

- in another terminal navigate to the project folder and type this command
    - python3 -m client_app.main
    - you should see this 
    1.Send formula 1
    2.Send formula 2 
    3.Send invalid formula
    4.Get all formulas
    - choose any option to test code

- These options allow you to :
    - get all formulas currently in the db, empty list if none
    - send formulas to see creation or duplication error
    - send incorrect formula schema to see validation error 

- to clear db while starting the application go to the app/main/py and uncomment drop_db in on_startup
