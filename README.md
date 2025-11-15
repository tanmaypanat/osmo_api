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
- Atomic operations - I decided to follow a simple solution for atomicity, which includes queue rollback on db write failure and no db write on queue failure, this avoids additional complexity which is used in production like outbox, cdc , db triggers etc
- pydantic for data validation
- aiohttp for async server
- sqlalchemy for handling data insertion. retrieval from db. This uses the datamodel and table schemas for insertion without writing    sql queries which are prone to typos
- postgres on docker - containarized example, makes it easier to use this way, user and db creation through docker file without explicit commands.

## Duplicate detection strategy 
### Client side
Note - I did not consider client side strategies as I am assuming I do not have control over client requests. I will focus on server side implementation. These just represent potential client side solutions.

1. Client side request uuid :-
- generate unique uuid, send it with header or message body as a identifier for same message.
- Resource  - https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs
2. Backoff and jitter, with uuid :-
- Realize that retries cause duplicate messages, implement exponential backoff and random jitter.
- Only retry for server side transient errors, not client side or persistent errors
- Use in combination with uuid to implement idempotency while not overwhelming the api 
- Resource - https://embedded.gusto.com/blog/defensive-programming-api-clients/
3. UI based button disable :-
- If client uses ui interface for submitting a request, deactivate button on click until api responds or timesout
- this avoid client clicking the button multiple times 
- Resource https://github.com/microsoft/microsoft-ui-xaml/discussions/9445

### Server side
There are 3-4 well recognized and recommended server side strategies these articles talk about the same 
https://leapcell.io/blog/building-robust-apis-preventing-duplicate-operations-with-idempotency
https://www.tencentcloud.com/techpedia/128055

1. Unique database constraints, database level 
- If data has unique identifier like order_id , or user with email_id that already exists , database can prevent insertion 
- Reason for not choosing this by itself
    - provided data does not have such a unique attribute.
    - Requires some db processing and insert failure to respond back to customer.
- I will be using this with number 3. for storing unique hashes, but main focus is on creating those unique hashes in 3.

2. Database locks
- not applicable as we do not have competing resource issue 

3. Canonical hashing 
- use a hash function to hash the body of the message 
- before hashing normalize data
    - remove whitespaces
    - address alphabet capitalization
    - address numeric values
    - address order of keys in message
- Why I chose this / why this works for our application 
    - we want to prevent duplication based on formulas
    - formulas have a fixed material field which has name and concentration 
    - This data can be easily normalized and we can expect the materials dict to not change schema, even if formulas change.
    - json hashing is sensitive to order, formulas compound names can be sorted and lower cased easily.
- Assumptions made 
    - Formula schema is unchanged 
    - it will always be in materials 
    - each compound will have name and concentration
    - We want to de duplicate on Formula only.
        - If we get a new message which has a different name, summer breeze vs summer delight, we will NOT create a new entry for summer delight if the formula is the same as summer breeze. 
        - Therefore exclude name of scent from hashing 
- Potential drawbacks
    - Json hashing is based on characters, it does not understand small differences like " summer" vs "summer" or 10.0 vs 10, so data normalization is important 
    - changing schema will invalidate older hashes 
        - eg new schema uses conc instead of concentration
        - Do we potentially normalize this too?

Understand that no one method is best. Idempotency should be handled at client and server side. Using uuid in conjunction with hashes and db restrictions adds layers of redundancy for effective data handling.


## Atomicity Strategies 
1. outbox - write message to two tables, actual formula table and outbox table 
- a background worked then reads from this table to publish onto a queue
- resource : https://www.shaunakc.com/blogs/the-outbox-pattern
2. cdc on outbox or db - change data capture 
- like 'emitting' changes on db, captured by debezium, forwarded to kafka
- Resource : https://medium.com/@subodh.shetty87/designing-reliable-distributed-systems-transactional-outbox-change-data-capture-cdc-pattern-0461b00cf059
3. What I used 
- I chose not to have all the additional overhead which comes with the above two strategies , as they either need additional software tools or additional worker and tables.
- Our application is straight forward with a single endpoint writing formulas 
- modern queues like kafka do not allow such rollback deletion but its easy to implement in a simple queue
- edge cases:
    - We do not have a consumer in the application, but if one existed, it can potentially consume the queued message before rollback
        -lock queue until db insert?
    - Retry mechanism - its serves a s proof of concept, in reality we need to know why the db is down and if retrying will help, a 0.1 sec sleep might not be enough
