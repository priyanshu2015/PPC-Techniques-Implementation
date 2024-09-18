# TODO
- Implement a gui for shamir secret sharing
- Implement a gui for homomorphic encryption
  - Implement a gui for the computation server
- Implement the zero-knowledge proof
  - Implement the zero-knowledge proof for the computation server
- Implement the secure multi-party computation between multiple bank servers
- write the documentation for the code
- integrate the gui with the bank server for click and run

# Bank Server

## Running the Bank Server
To run the Bank Server, you need to have Python 3.19 installed on your machine.
Then run the following commands.
```
cd Computation_Server 
python app.py
```

## Folder Structure
The app folder contains all the source code for the Bank Server.
The database folder contains the database schema and the database connection file and also
a controller file for the database connection.

The run.py file is the entry point for the Bank Server.
The database folder contains the database schema and the database controller and a file to generate
random data for the database.

The app folder contains the following :
- \_\_init\_\_.py:
  - This file initializes the app and contains all the routes for the app.

- data:
  - This folder contains the simple api to access the database.

- homomorphic_encryption:
  - This folder contains the homomorphic encryption implementation.
  - The file "homomorphic_encryption.py" contains the implementation of the homomorphic encryption.
  - The file "routes.py" contains the routes for the homomorphic encryption.

- main:
  - the "/users_page" route renders the user database table
  - the "/transactions_page" route renders the transactions database table

- smpc:
  - This folder contains the secure multi-party computation implementation.
  - The file "shamir_secret_sharing.py" contains the implementation of the secure multi-party computation.
  - The file "routes.py" contains the routes for the secure multi-party computation.

- zero_knowledge_proof:
  - This folder contains the zero-knowledge proof implementation.
  - To be implemented in the future for something
  - I thought about implementing it to authenticate at the computation server

- templates:
  - This folder contains the html files for the routes.

# Computation Server
- Server to perform the homomorphic encryption.
- has some routes to perform the homomorphic encryption.
