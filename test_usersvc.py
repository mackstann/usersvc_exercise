import pytest, uuid, json

import usersvc

@pytest.fixture
def client():
    usersvc.app.config['TESTING'] = True
    with usersvc.app.test_client() as client:
        with usersvc.app.app_context():
            usersvc.reset_db()
        yield client

def dicts_same_except(d1, d2, ignore):
    """
    Checks if dicts d1 and d2 are equal, but ignoring keys specified in the ignore list.
    """
    d1 = d1.copy()
    d2 = d2.copy()
    for k in ignore:
        try:
            del d1[k]
        except KeyError:
            pass
        try:
            del d2[k]
        except KeyError:
            pass
    return d1 == d2

### empty data tests

def test_list_empty_db(client):
    resp = client.get('/users')
    assert resp.status_code == 200
    assert ('Content-Type', 'application/json') in resp.headers.items()
    assert resp.get_json() == []

def test_get_nonexistent(client):
    resp = client.get('/users/'+str(uuid.uuid4()))
    assert resp.status_code == 404

def test_patch_nonexistent(client):
    resp = client.patch('/users/'+str(uuid.uuid4()))
    assert resp.status_code == 404

def test_delete_nonexistent(client):
    resp = client.delete('/users/'+str(uuid.uuid4()))
    assert resp.status_code == 404

### basic "happy path" tests

def test_post(client):
    # When I create a user
    expected_user = {'firstname': 'The', 'lastname': 'Doctor', 'email': 'a@b.com', 'zipcode': '97204'}
    resp = client.post('/users', data=json.dumps(expected_user), content_type='application/json')
    assert resp.status_code == 201
    assert ('Content-Type', 'application/json') in resp.headers.items()

    # Then the response contains the attributes I submitted, plus a generated ID
    actual_user = resp.get_json()
    assert dicts_same_except(actual_user, expected_user, ['id'])
    assert str(uuid.UUID(actual_user['id'])) == actual_user['id']

def test_get(client):
    # Given I have created a user
    expected_user = {'firstname': 'The', 'lastname': 'Doctor', 'email': 'a@b.com', 'zipcode': '97204'}
    resp = client.post('/users', data=json.dumps(expected_user), content_type='application/json')
    assert resp.status_code == 201
    actual_user = resp.get_json()

    # When I fetch the user
    resp = client.get('/users/'+actual_user['id'])
    assert resp.status_code == 200
    assert ('Content-Type', 'application/json') in resp.headers.items()

    # Then I see the user contains the attributes I submitted, plus a generated ID
    actual_user = resp.get_json()
    assert dicts_same_except(actual_user, expected_user, ['id'])
    assert str(uuid.UUID(actual_user['id'])) == actual_user['id']

def test_patch(client):
    # each of these is a PATCH body that will be exercised
    cases = [
        {'firstname': 'Nick'},
        {'lastname': 'Welch'},
        {'zipcode': '12345'},
        {'email': 'foo@bar.com'},
        {'firstname': 'Multiple', 'zipcode': '99999-1234'},
    ]

    for patch in cases:
        # Given I have created a user
        expected_user = {'firstname': 'The', 'lastname': 'Doctor', 'email': 'a@b.com', 'zipcode': '97204'}
        resp = client.post('/users', data=json.dumps(expected_user), content_type='application/json')
        assert resp.status_code == 201
        actual_user = resp.get_json()

        # When I update the user
        resp = client.patch('/users/'+actual_user['id'], data=json.dumps(patch), content_type='application/json')
        assert resp.status_code == 204
        assert resp.data == b''

        # And I re-fetch the user
        resp = client.get('/users/'+actual_user['id'])
        assert resp.status_code == 200
        updated_user = resp.get_json()
        assert ('Content-Type', 'application/json') in resp.headers.items()

        # Then I see the specified fields in the user have been updated
        changed_fields = list(patch.keys())
        assert dicts_same_except(updated_user, expected_user, ['id']+changed_fields)
        assert str(uuid.UUID(actual_user['id'])) == actual_user['id']
        for k, v in patch.items():
            assert updated_user[k] == v

def test_delete(client):
    # Given I have created a user
    expected_user = {'firstname': 'The', 'lastname': 'Doctor', 'email': 'a@b.com', 'zipcode': '97204'}
    resp = client.post('/users', data=json.dumps(expected_user), content_type='application/json')
    assert resp.status_code == 201
    actual_user = resp.get_json()

    # When I delete the user
    resp = client.delete('/users/'+actual_user['id'])
    assert resp.status_code == 204
    assert resp.data == b''

    # And I try to re-fetch the user
    resp = client.get('/users/'+actual_user['id'])

    # Then I receive a Not Found error
    assert resp.status_code == 404

### input validation, corner cases, etc.

# more stuff that would be good to implement/test:
# * prohibit non-printable characters
# * strip leading/trailing whitespace
# * multiple validation errors in the same request
bad_input_cases = [
    ({'firstname': 'x'*1000}, 'firstname too long'),
    ({'lastname': 'x'*1000}, 'lastname too long'),
    ({'zipcode': '1234'}, 'zipcode must be formatted as either NNNNN or NNNNN-NNNN'),
    ({'email': 'foo-at-bar.com'}, 'invalid email'),
    ({'firstname': 'Multiple', 'zipcode': 'AAAAA-1234'}, 'zipcode must be formatted as either NNNNN or NNNNN-NNNN'),
]

def test_post_invalid(client):
    for bad_attrs, expected_msg in bad_input_cases:
        expected_user = {'firstname': 'The', 'lastname': 'Doctor', 'email': 'a@b.com', 'zipcode': '97204'}
        expected_user.update(bad_attrs)
        resp = client.post('/users', data=json.dumps(expected_user), content_type='application/json')
        assert resp.status_code == 400
        assert resp.get_json() == {'error': expected_msg}

def test_patch_invalid(client):
    for patch, expected_msg in bad_input_cases:
        expected_user = {'firstname': 'The', 'lastname': 'Doctor', 'email': 'a@b.com', 'zipcode': '97204'}
        resp = client.post('/users', data=json.dumps(expected_user), content_type='application/json')
        assert resp.status_code == 201
        actual_user = resp.get_json()

        resp = client.patch('/users/'+actual_user['id'], data=json.dumps(patch), content_type='application/json')
        assert resp.status_code == 400
        assert resp.get_json() == {'error': expected_msg}
