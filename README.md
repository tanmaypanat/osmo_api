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

- To clear db while starting the application go to the app/main/py and uncomment drop_db in on_startup

# Design Decisions
- Idempotency - Json message body hashing with db unique hash store in postgres, redis if time permits implementation. 
- Atomic operations - I decided to follow a simple solution for atomicity, which includes queue rollback on db write failure and no db write on queue failure, this avoid additional complexity which is used in production like outbox, cdc , db triggers etc
- pydantic for data validation
- aiohttp for async server
- sqlalchemy for handling data insertion. retrieval from db. This uses the datamodel and table schemas for insertion without writing    sql queries which are prone to typos
- postgres on docker - contanarized example plus makes it easier to use this way, user and db creation through docker file without explicit commands.

## Duplicate detection strategy 
### client side
Note - I did not consider client side strategies as I am assuming I do not have control over client requests. I will focus on server side implementation. These just represent potential client side solutions.

1. Client side request uuid :-
generate unique uuid, send it with header or message body as a identifier for same message.
Resource  - https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs
2. Backoff and jitter, with uuid :-
Realize that retries cause duplicate messages, implement exponential backoff and random jitter.
Only retry for server side transient errors, not client side or persistent errors
Use in combination with uuid to implement idempotency while not overwhelming the api 
Resource -
https://embedded.gusto.com/blog/defensive-programming-api-clients/
3. UI based button disable :-
If client uses ui interface for submitting a request, deactivate button on click until api responds or timesout
this avoid client clicking the button multiple times 
Resource 
https://github.com/microsoft/microsoft-ui-xaml/discussions/9445

