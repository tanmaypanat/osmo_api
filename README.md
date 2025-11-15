# osmo_api
Repository for osmo take home assignment 

Setup and testing instructions
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