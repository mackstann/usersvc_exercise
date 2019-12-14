import re, uuid

from flask import Flask, request, abort, url_for
from flask.json import jsonify

app = Flask(__name__)

### Model and persistence

class User:
    # I would use a namedtuple to reduce boilerplate here, but my local Python isn't new enough.
    def __init__(self, id, firstname, lastname, zipcode, email):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.zipcode = zipcode
        self.email = email

    def to_dict(self):
        return {
            attr: getattr(self, attr)
            for attr in ('id', 'firstname', 'lastname', 'zipcode', 'email')
        }

db = {}

def reset_db():
    db.clear()

def debug_print_db(db):
    print("----- Database dump -----")
    print("{} users:".format(len(db)))
    for u in db.values():
        print("    {}".format(u.to_dict()))
    print("----- End -----")

### Input validation & request error handling

class ValidationError(ValueError):
    pass

def error(msg):
    return {'error': msg}

reasonable_length = 50

zip_pattern = re.compile(r'^\d{5}(-\d{4})?$')

# this is a crude sanity check. to fully parse and validate an email address is famously complicated:
# http://www.ex-parrot.com/pdw/Mail-RFC822-Address.html
email_pattern = re.compile(r'.+@.+')

def validate_user(form):
    if len(form.get('firstname', '')) > reasonable_length:
        raise ValidationError("firstname too long")
    if len(form.get('lastname', '')) > reasonable_length:
        raise ValidationError("lastname too long")

    zipcode = form.get('zipcode')
    if zipcode and not zip_pattern.match(zipcode):
        raise ValidationError("zipcode must be formatted as either NNNNN or NNNNN-NNNN")

    email = form.get('email', '')
    if len(email) > reasonable_length:
        raise ValidationError("email too long")
    print(email)
    if email and not email_pattern.match(email):
        raise ValidationError("invalid email")

### Route handlers

@app.route("/users/<id>", methods=["GET"])
def get_user(id):
    try:
        return jsonify(db[id].to_dict())
    except KeyError:
        return abort(404)

@app.route("/users", methods=["GET"])
def list_users():
    return jsonify([ u.to_dict() for u in db.values() ])

@app.route("/users", methods=["POST"])
def create_user():
    if not request.is_json:
        return jsonify(error('Request Content-Type must be application/json')), 400

    form = request.get_json()
    try:
        validate_user(form)
    except ValidationError as e:
        return jsonify(error(str(e))), 400

    user = User(
        id=str(uuid.uuid4()),
        firstname=form.get('firstname', ''),
        lastname=form.get('lastname', ''),
        zipcode=form.get('zipcode', ''),
        email=form.get('email', ''),
    )
    db[user.id] = user
    debug_print_db(db)

    # typical HTTP 201 Created response
    headers = {'Location': url_for('get_user', id=id)}
    return jsonify(user.to_dict()), 201, headers

@app.route("/users/<id>", methods=["PATCH"])
def update_user(id):
    try:
        user = db[id]
    except KeyError:
        return abort(404)

    if not request.is_json:
        return jsonify(error('Request Content-Type must be application/json')), 400
    form = request.get_json()

    try:
        validate_user(form)
    except ValidationError as e:
        return jsonify(error(str(e))), 400

    def maybe_update_field(user, form, attr):
        # this eliminates some repetition, but in the real world this might lead to undesirable coupling between the
        # attribute names exposed in the API and the attribute names in the model implementation -- they wouldn't always
        # necessarily be the same.
        if attr in form and form[attr] != getattr(user, attr):
            setattr(user, attr, form[attr])

    maybe_update_field(user, form, 'firstname')
    maybe_update_field(user, form, 'lastname')
    maybe_update_field(user, form, 'zipcode')
    maybe_update_field(user, form, 'email')

    db[id] = user
    debug_print_db(db)

    return '', 204 # HTTP 204 No Content. Returning 200 with a body would also be valid.

@app.route("/users/<id>", methods=["DELETE"])
def delete_user(id):
    try:
        del db[id]
    except KeyError:
        return abort(404)
    debug_print_db(db)
    return '', 204
