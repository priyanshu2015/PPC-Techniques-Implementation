# TODO
- Implement the zero-knowledge proof
- Implement the secure multi-party computation between multiple bank servers
- write the documentation for the code
- integrate the gui with the bank server for click and run

# Bank Server
The app folder contains all the source code for the Bank Server.
The database folder contains the database schema and the database connection file and also
a controller file for the database connection.

The app folder contains the following folders:
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