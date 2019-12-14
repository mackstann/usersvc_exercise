# usersvc_exercise
Microservice built as a code exercise.

# How to Build and Run

This project uses Python 3, so be careful not to accidentally use Python 2 if you have it installed.

    virtualenv env # or maybe virtualenv-3 depending on your OS/package situation
    source env/bin/activate
    pip install -r requirements.txt
    FLASK_APP=usersvc.py flask run

## Run the test suite

```
% pytest -vv
===================================================== test session starts =====================================================
platform linux -- Python 3.6.5, pytest-5.3.1, py-1.8.0, pluggy-0.13.1 -- /home/vagrant/usersvc_exercise/env/bin/python3
cachedir: .pytest_cache
rootdir: /home/vagrant/usersvc_exercise
plugins: cov-2.8.1
collected 10 items

test_usersvc.py::test_list_empty_db PASSED                                                                              [ 10%]
test_usersvc.py::test_get_nonexistent PASSED                                                                            [ 20%]
test_usersvc.py::test_patch_nonexistent PASSED                                                                          [ 30%]
test_usersvc.py::test_delete_nonexistent PASSED                                                                         [ 40%]
test_usersvc.py::test_post PASSED                                                                                       [ 50%]
test_usersvc.py::test_get PASSED                                                                                        [ 60%]
test_usersvc.py::test_patch PASSED                                                                                      [ 70%]
test_usersvc.py::test_delete PASSED                                                                                     [ 80%]
test_usersvc.py::test_post_invalid PASSED                                                                               [ 90%]
test_usersvc.py::test_patch_invalid PASSED                                                                              [100%]

===================================================== 10 passed in 0.25s ======================================================

```

## Run the coverage report

```
% pytest --cov=usersvc test_usersvc.py
===================================================== test session starts =====================================================
platform linux -- Python 3.6.5, pytest-5.3.1, py-1.8.0, pluggy-0.13.1
rootdir: /home/vagrant/usersvc_exercise
plugins: cov-2.8.1
collected 10 items

test_usersvc.py ..........                                                                                              [100%]

----------- coverage: platform linux, python 3.6.5-final-0 -----------
Name         Stmts   Miss  Cover
--------------------------------
usersvc.py     113      3    97%


===================================================== 10 passed in 0.35s ======================================================
```

## HTTP Usage Demo

```
curl -X "POST" "http://localhost:5000/users" -H "Content-Type: application/json" -d '{"firstname":"The","lastname":"Doctor","zipcode":"97204","email":"x@b.com"}'
{
  "email": "x@b.com",
  "firstname": "The",
  "id": "7d79020d-1b07-4baa-858a-28bfe1cc1e25",
  "lastname": "Doctor",
  "zipcode": "97204"
}

% curl -X "GET" "http://localhost:5000/users/7d79020d-1b07-4baa-858a-28bfe1cc1e25"
{
  "email": "x@b.com",
  "firstname": "The",
  "id": "7d79020d-1b07-4baa-858a-28bfe1cc1e25",
  "lastname": "Doctor",
  "zipcode": "97204"
}

% curl -X "PATCH" "http://localhost:5000/users/7d79020d-1b07-4baa-858a-28bfe1cc1e25" -H "Content-Type: application/json" -d '{"firstname":"Da"}'
% curl -X "GET" "http://localhost:5000/users/7d79020d-1b07-4baa-858a-28bfe1cc1e25"
{
  "email": "x@b.com",
  "firstname": "Da",
  "id": "7d79020d-1b07-4baa-858a-28bfe1cc1e25",
  "lastname": "Doctor",
  "zipcode": "97204"
}

% curl -X "DELETE" "http://localhost:5000/users/7d79020d-1b07-4baa-858a-28bfe1cc1e25"
% curl -X "GET" "http://localhost:5000/users/7d79020d-1b07-4baa-858a-28bfe1cc1e25"
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>

```

(That 404 should ideally return a JSON body, not HTML.)

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
