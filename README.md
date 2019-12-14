# usersvc_exercise
Microservice built as a code exercise.

# How to Build and Run

This project uses Python 3, so be careful not to accidentally use Python 2 if you have it installed.

    virtualenv env # or maybe virtualenv-3 depending on your OS/package situation
    source env/bin/activate
    pip install -r requirements.txt
    FLASK_APP=usersvc.py flask run

# Features

* A User rest Resource that allows clients to create, read, update, delete a user or a list of users.
    * I found some ambiguity in this sentence: which parts need to support a list of users? Would you delete a list of
      users? Update a list? Create a list? These seem a little unusual (but still plausible), so I would ideally get
      clarification before implementing list operations, so I'm not building unwanted functionality. Until/unless I get
      clarification, I'll assume a typical REST interface:
        * `GET /users` lists all users
	* `GET /users/:id` returns one user
	* `POST/PATCH/DELETE /users/:id` operate on one user
* For simplicity, the database will be a simple dict that is not persisted.
* A user resource contains:
    * id
    * first name
    * last name
    * zip code
    * email address
* I intentionally omitted features that weren't requested, for example:
    * Authentication
    * Authorization
    * Ordering/sorting of results
    * Filtering
    * Pagination
    * API docs, e.g. Swagger
* I did implement some input validation, because it's not too complicated, and accepting garbage data is pretty sad,
  even in a toy project.

# Design

Normally I might've used something like the `flask_restplus` package, which helps streamline things like input
validation and documentation generation, but I haven't used it before, so I stuck with vanilla Flask just to avoid
dragging out this exercise too much.

The tests are very barebones pytest tests. I've been writing Cucumber/Gherkin tests for a while, so I found it helpful
(at least to me) to throw some Gherkin in comments to help organize and explain what's going on. It'd probably be nicer
to use a real Python BDD library.

In a real project, I would also try to separate the code into layers to better separate concerns, e.g. a business logic
layer, a storage layer, an HTTP layer, etc.

# Notes/Thoughts

In a real user service, security and privacy would be top concerns, and would impact the design:

* Would you ever really need to list all users in the database? Maybe not. I would be interested in omitting that
  feature. The ability to list an entire database's worth of names, zips, and emails would be a target for attacks.
* Maybe even consider rate limiting?
* Authentication and Authorization would be important, to ensure that not just anyone can go snooping on other users'
  information, or tampering with data.
* More robust input validation would be a good thing.
* Logging things like email addresses also requires some care.
