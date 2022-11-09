'''Test cases for language related APIs'''
from sqlalchemy.orm import Session
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get
from .test_auth_basic import SUPER_USER,SUPER_PASSWORD, login, logout_user
from .conftest import initial_test_users

UNIT_URL = '/v2/languages'

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "languageId" in item
    assert isinstance(item['languageId'], int)
    assert "language" in item
    assert "code" in item
    assert "scriptDirection" in item
    if "metaData" in item and item['metaData'] is not None:
        assert isinstance(item['metaData'], dict)

def test_get_default():
    '''positive test case, without optional params'''
    headers = {"contentType": "application/json", "accept": "application/json"}
    check_default_get(UNIT_URL, headers,assert_positive_get)

def test_get_language_code():
    '''positive test case, with one optional params, code wihtout registered user'''
    response = client.get(UNIT_URL+'?language_code=hi')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['code'] == 'hi'

    #with registred user header
    headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.get(UNIT_URL+'?language_code=hi',headers=headers_auth)
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['code'] == 'hi'


def test_get_language_code_upper_case():
    '''positive test case, with one optional params, code in upper case'''
    response = client.get(UNIT_URL+'?language_code=HI')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['code'] == 'hi'

def test_get_language_name():
    '''positive test case, with one optional params, name'''
    response = client.get(UNIT_URL+'?language_name=hindi')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['language'].lower() == 'hindi'

def test_get_language_name_mixed_case():
    '''positive test case, with one optional params, name, with first letter capital'''
    response = client.get(UNIT_URL+'?language_name=Hindi')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['language'].lower() == 'hindi'

def test_get_multiple_params():
    '''positive test case, with two optional params'''
    response = client.get(UNIT_URL+'?language_name=hindi&language_code=hi')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['language'].lower() == 'hindi'
    assert response.json()[0]['code'] == 'hi'

def test_get_notavailable_language():
    ''' request a not available language, with code'''
    response = client.get(UNIT_URL+"?language_code=aaj")
    assert_not_available_content(response)

def test_get_notavailable_language2():
    ''' request a not available language, with language name'''
    response = client.get(UNIT_URL+"?language_name=not-a-language")
    assert_not_available_content(response)

def test_get_incorrectvalue_language_code():
    '''language code should be letters'''
    response = client.get(UNIT_URL+"?language_code=110")
    assert_input_validation_error(response)

def test_get_incorrectvalue_language_code2():
    '''language code should have exactly 3 letters'''
    response = client.get(UNIT_URL+"?language_code='abcd.10'")
    assert_input_validation_error(response)

def test_post_default():
    '''positive test case, checking for correct return object'''
    data = {
      "language": "new-lang",
      "code": "x-aaj",
      "scriptDirection": "left-to-right"
    }
    #Add Language without Auth
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #Add with Auth
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Language created successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["code"] == "x-aaj"

def test_post_upper_case_code():
    '''positive test case, checking for case conversion of code'''
    data = {
      "language": "new-lang",
      "code": "X-AAJ",
      "scriptDirection": "left-to-right"
    }
    #Add Language without Auth
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #Add with Auth
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Language created successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["code"] == "X-AAJ"

def test_post_optional_script_direction():
    '''positive test case, checking for correct return object'''
    data = {
      "language": "new-lang",
      "code": "x-aaj"
    }
    #Add without Auth
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #Add with Auth
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Language created successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["code"] == "x-aaj"


def test_post_incorrectdatatype1():
    '''code should have letters only'''
    data = {
      "language": "new-lang",
      "code": "123",
      "scriptDirection": "left-to-right"
    }
    #Add with Auth
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_post_incorrectdatatype2():
    '''scriptDirection should be either left-to-right or right-to-left'''
    data = {
      "language": "new-lang",
      "code": "MMM",
      "scriptDirection": "regular"
    }
    #Add with Auth
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_post_missingvalue_language():
    '''language name should be present'''
    data = {
      "code": "MMM",
      "scriptDirection": "left-to-right"
    }
    #Add with Auth
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_put_languages():
    """put test for languages"""
    #create a new langauge
    data = {
      "language": "new-lang-test",
      "code": "x-abc"
    }
    #Add with Auth
    headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Language created successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["code"] == "x-abc"

    #get language id
    response = client.get(UNIT_URL+'?language_code=x-abc')
    assert response.status_code == 200
    language_id = response.json()[0]['languageId']

    #edit with created user
    data = {
      "languageId": language_id,
      "language": "new-lang-test-edited",
      "code": "x-abc"
    }
    response = client.put(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Language edited successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["language"] == "new-lang-test-edited"

    # #delete the user
    # delete_user_identity(test_user_id)

    #edit without login
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.put(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == "Authentication Error"

    #create a new user and edit the previous user created content
    headers_auth2 = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser']['token']
            }
    response = client.put(UNIT_URL, headers=headers_auth2, json=data)
    assert response.status_code == 403
    assert response.json()['error'] == "Permission Denied"

    #super admin can edit the content
    data_admin   = {
    "user_email": SUPER_USER,
    "password": SUPER_PASSWORD
    }
    response =login(data_admin)
    assert response.json()['message'] == "Login Succesfull"
    token_admin =  response.json()['token']

    data = {
      "languageId": language_id,
      "language": "new-lang-test-edited-by-admin",
      "code": "x-abc"
    }
    headers_admin = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
            }
    response = client.put(UNIT_URL, headers=headers_admin, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Language edited successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["language"] == "new-lang-test-edited-by-admin"

    logout_user(token_admin)

def test_searching():
    '''Being able to query languages with code, name, country of even other info'''

    response = client.get(UNIT_URL+"?search_word=ml")
    assert len(response.json()) > 0
    found = False
    for lang in response.json():
        assert_positive_get(lang)
        if lang['code'] == "ml":
            found = True
    assert found

    response = client.get(UNIT_URL+"?search_word=india")
    assert len(response.json()) > 0
    found = False
    for lang in response.json():
        assert_positive_get(lang)
        if lang['code'] == "hi":
            found = True
    assert found
    response = client.get(UNIT_URL+"?search_word=sri%20lanka")
    assert len(response.json()) > 0
    found = False
    for lang in response.json():
        assert_positive_get(lang)
        if lang['language'] == "Sinhala":
            found = True
    assert found

    # search word with special symbols in them
    response = client.get(UNIT_URL+"?search_word=sri%20lanka(Asia)")
    assert len(response.json()) > 0
    found = False
    for lang in response.json():
        assert_positive_get(lang)
        if lang['language'] == "Sinhala":
            found = True
    assert found

    response = client.get(UNIT_URL+"?search_word=sri-lanka-asia!")
    assert len(response.json()) > 0
    found = False
    for lang in response.json():
        assert_positive_get(lang)
        if lang['language'] == "Sinhala":
            found = True
    assert found

    # ensure search words are not stemmed as per rules of english
    response = client.get(UNIT_URL+"?search_word=chinese")
    assert len(response.json()) > 5

def populate_language_db(db_ : Session): # pylint: disable=C0116
    db_.execute('''INSERT INTO languages(language_code,language_name,script_direction)\
     VALUES ('x-aaj','new-lang','left-to-right')''')
    db_.commit()
    lang_id = db_.execute('''SELECT language_id FROM languages \
    WHERE (language_code = 'x-aaj')''')
    db_.commit()
    [test_language_id] = lang_id.fetchone()
    return test_language_id

def test_delete_default():
    ''' positive test case, checking for correct return of deleted content ID'''
    #Registerd User can only delete language
    #Delete language without auth
    data = {
      "language": "new-lang",
      "code": "x-abc",
      "scriptDirection": "left-to-right"
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 422
    #Delete Language with Auth
    #Insert New Language
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 201

    #get language id
    response = client.get(UNIT_URL+'?language_code=x-abc')
    assert response.status_code == 200
    language_id = response.json()[0]['languageId']
    #delete language
    delete_data = {"languageId":language_id}
    response = client.delete(UNIT_URL, headers=headers, json=delete_data)
    assert response.status_code == 200
    assert response.json()['message'] ==\
    f"Language with identity {language_id} deleted successfully"

def test_delete_language_id_string():
    '''positive test case, language id as string'''
    data = {
      "language": "new-lang",
      "code": "x-abc",
      "scriptDirection": "left-to-right"
    }
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 201

    #get language id
    response = client.get(UNIT_URL+'?language_code=x-abc')
    assert response.status_code == 200
    language_id = response.json()[0]['languageId']
    #delete language
    lang_id = str(language_id)
    data = {"languageId": lang_id}
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 200
    assert response.json()['message'] == f"Language with identity {lang_id} deleted successfully"


def test_delete_incorrectdatatype():
    '''the input data object should a json with "languageId" key within it'''
    data = 100100
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_delete_missingvalue_language_id():
    '''languageId is mandatory in input data object'''
    data = {}
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_delete_notavailable_language_id():
    ''' request a non existing content ID, Ensure there is not partial matching'''
    data = {"languageId":1000}
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL,headers=headers,json=data)
    assert response.status_code == 502
    assert response.json()['error'] == "Database Error"
