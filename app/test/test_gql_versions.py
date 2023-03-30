"""Test cases for Versions GQL"""
from typing import Dict

#pylint: disable=E0401
from app.schema import schema_auth
from .test_versions import assert_positive_get
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import  check_skip_limit_gql, gql_request,assert_not_available_content_gql
from .conftest import initial_test_users

headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                "App":schema_auth.App.VACHANADMIN.value,
                "Authorization": "Bearer "+initial_test_users["VachanAdmin"]["token"]}
headers = {"contentType": "application/json", "accept": "application/json"}

GLOBAL_VARIABLES = {
    "object": {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "versionTag": "1",
        "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
    }
    }

GLOBAL_QUERY = """
    mutation createversion($object:InputAddVersion){
    addVersion(versionArg:$object){
        message
        data{
        versionId
        versionAbbreviation
        versionName
        versionTag
        metaData
        }
    }
    }
    """

def check_post(query, variables):
    """common for check post"""
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
    headers_auth['App'] = schema_auth.App.VACHANADMIN.value
    #without auth
    executed = gql_request(query=query,operation="mutation", variables=variables)
    assert "errors" in executed.keys()
    #with auth
    executed = gql_request(query=query,operation="mutation", variables=variables,
    headers=headers_auth)
    assert isinstance(executed, Dict)
    assert executed["data"]["addVersion"]["message"] == "Version created successfully"
    item =executed["data"]["addVersion"]["data"]
    # print("Created Version Data ============>",item)
    item["versionId"] = int(item["versionId"])
    assert_positive_get(item)
    assert item["versionAbbreviation"] == variables["object"]["versionAbbreviation"]
    return executed

def assert_error_check(query, variables):
    """common error check"""
    executed = gql_request(query=query,operation="mutation", variables=variables,
    headers=headers_auth)
    assert "errors" in executed.keys()

def test_post_default():
    '''Positive test to add a new version'''
    check_post(GLOBAL_QUERY,GLOBAL_VARIABLES)

def check_skip_limit():
    """chekc skip and limit add multiple versions"""

    check_post(GLOBAL_QUERY,GLOBAL_VARIABLES)

    var1 = {
    "object": {
        "versionAbbreviation": "ABC",
        "versionName": "ABC version to test",
    }
    }

    var2 = {
    "object": {
        "versionAbbreviation": "EFG",
        "versionName": "EFG version to test",
    }
    }

    check_post(GLOBAL_QUERY,var1)
    check_post(GLOBAL_QUERY,var2)
    
    query_check = """
        {
         query versions($skip:Int, $limit:Int){
  versions(skip:$skip,limit:$limit){
    versionAbbreviation
  }
}
    """
    check_skip_limit_gql(query_check,"versions")

def test_post_multiple_with_same_abbr():
    '''Positive test to add two version, with same abbr and diff versionTag'''
    variables = GLOBAL_VARIABLES
    variables["object"]["versionTag"] = "2"
    check_post(GLOBAL_QUERY,variables)

def test_post_multiple_with_same_abbr_negative():
    '''Negative test to add two version, with same abbr and versionTag'''
    check_post(GLOBAL_QUERY,GLOBAL_VARIABLES)
    executed2 =  gql_request(query=GLOBAL_QUERY,operation="mutation", variables=GLOBAL_VARIABLES,
    headers=headers_auth)
    assert isinstance(executed2, Dict)
    assert "errors" in executed2.keys()

def test_post_without_versionTag():
    '''versionTag field should have a default value, even not provided'''
    variables = {
    "object": {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
    }
    }
    executed = check_post(GLOBAL_QUERY,variables)
    assert executed["data"]["addVersion"]["data"]["versionTag"] == "1"

def test_post_without_metadata():
    '''metadata field is not mandatory'''
    variables = {
    "object": {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "versionTag": "1"
    }
    }
    executed = check_post(GLOBAL_QUERY,variables)
    assert executed["data"]["addVersion"]["data"]["metaData"] is None

def test_post_without_abbr():
    '''versionAbbreviation is mandatory'''
    variables = {
    "object": {
        "versionName": "Xyz version to test",
        "versionTag": "1"
    }
    }
    assert_error_check(GLOBAL_QUERY,variables)

def test_post_wrong_abbr():
    '''versionAbbreviation cannot have space, dot etc'''
    variables = {
    "object": {
        "versionAbbreviation": "XY Z",
        "versionName": "Xyz version to test",
        "versionTag": "1"
    }
    }
    assert_error_check(GLOBAL_QUERY,variables)

    variables2 = {
    "object": {
        "versionAbbreviation": "XY.Z",
        "versionName": "Xyz version to test",
        "versionTag": "1"
    }
    }
    assert_error_check(GLOBAL_QUERY,variables2)

def test_post_wrong_versionTag():
    '''versionTag cannot have space, comma, letters etc'''
    variables = {
    "object": {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "versionTag": "1"
    }
    }

    variables["object"]["versionTag"] = "1 2"
    assert_error_check(GLOBAL_QUERY,variables)

    # variables["object"]["versionTag"] = "1a"
    # assert_error_check(GLOBAL_QUERY,variables)

    variables["object"]["versionTag"] = "1,2"
    assert_error_check(GLOBAL_QUERY,variables)

def test_post_without_name():
    '''versionName is mandatory'''
    variables = {
    "object": {
        "versionAbbreviation": "XYZ",
        "versionTag": "1"
    }
    }
    assert_error_check(GLOBAL_QUERY,variables)

QUERY_GET = """
    {
    versions{
        versionId
        versionAbbreviation
        versionName
        versionTag
        metaData
    }
    }
"""

def test_get():
    '''Test get before adding data to table. Usually run on new test DB on local or github.
    If the testing is done on a DB that already has data(staging), the response wont be empty.'''
    headers_auth['App'] = schema_auth.App.API.value
    headers_auth['Authorization'] = "Bearer "+initial_test_users['APIUser']['token']
    executed =  gql_request(query=QUERY_GET,headers=headers_auth)
    if len(executed["data"]["versions"]) == 0:
        assert_not_available_content_gql(executed["data"]["versions"])

def test_get_wrong_abbr():
    '''abbreviation with space, number'''
    query = """
        {
    versions(versionAbbreviation:"A A"){
        versionId
        versionAbbreviation
        versionName
        versionTag
        metaData
    }
    }
    """
    executed =  gql_request(query=query,headers=headers_auth)
    assert_not_available_content_gql(executed["data"]["versions"])

    query2 = """
        {
    versions(versionAbbreviation:123){
        versionId
        versionAbbreviation
        versionName
        versionTag
        metaData
    }
    }
    """
    executed =  gql_request(query=query2)
    assert "errors" in executed.keys()

def test_get_wrong_versionTag():
    '''versionTag as text'''
    query = """
        {
    versions(version_tag:"red@1"){
        versionId
        versionAbbreviation
        versionName
        versionTag
        metaData
    }
    }
    """
    executed =  gql_request(query=query,headers=headers_auth)
    assert "errors" in executed.keys()

def test_get_after_adding_data():
    '''Add some data to versions table and test get method'''
    variables = {
    "object": {
       'versionAbbreviation': "AAA",
        'versionName': 'test name A',
        'versionTag': "1"
    }
    }
    check_post(GLOBAL_QUERY,variables)
    variables["object"]["versionTag"] = "2"
    check_post(GLOBAL_QUERY,variables)

    variables2 = {
    "object": {
        'versionAbbreviation': "BBB",
        'versionName': 'test name B',
        'versionTag': "1"
    }
    }
    check_post(GLOBAL_QUERY,variables2)
    variables2["object"]["versionTag"] = "2"
    check_post(GLOBAL_QUERY,variables2)

    #get added versions
    query_get_version_added = """
        query get_version($VAbb:String){
        versions(versionAbbreviation:$VAbb){
    versionId
    versionAbbreviation
    versionName
    versionTag
    metaData
  }
}
    """ 
    get_version_var = {
    "VAbb": "AAA"
    }
    headers_auth['App'] = schema_auth.App.API.value
    headers_auth['Authorization'] = "Bearer "+initial_test_users['APIUser']['token']
    executed_get = gql_request(query_get_version_added,variables=get_version_var,
    headers=headers_auth)
    assert isinstance(executed_get, Dict)
    assert len(executed_get["data"]["versions"]) == 2
    items =executed_get["data"]["versions"]
    for item in items:
        if 'versionId' in item:
            item["versionId"] = int(item["versionId"])
            assert_positive_get(item)

    get_version_var = {
    "VAbb": "BBB"
    }

    executed_get = gql_request(query_get_version_added,variables=get_version_var,
    headers=headers_auth)
    assert isinstance(executed_get, Dict)
    assert len(executed_get["data"]["versions"]) == 2
    items =executed_get["data"]["versions"]
    for item in items:
        if 'versionId' in item:
            item["versionId"] = int(item["versionId"])
            assert_positive_get(item)        

    #get test after successfull creation
    # filter with abbr
    query1 = """
            {
    versions(versionAbbreviation:"AAA"){
        versionId
        versionAbbreviation
        versionName
        versionTag
        metaData
    }
    }
    """
    executed1 = gql_request(query1)
    assert isinstance(executed1, Dict)
    items =executed1["data"]["versions"]
    for item in items:
        if 'versionId' in item:
            item["versionId"] = int(item["versionId"])
            assert_positive_get(item)
        assert item["versionAbbreviation"] == "AAA"

    # filter with abbr, for not available content
    query2 = """
            {
    versions(versionAbbreviation:"SSS"){
        versionId
        versionAbbreviation
        versionName
        versionTag
        metaData
    }
    }
    """
    executed2 = gql_request(query2)
    assert_not_available_content_gql(executed2["data"]["versions"])

    # filter with name
    query3 = """
            {
    versions(versionName:"test name B"){
        versionId
        versionAbbreviation
        versionName
        versionTag
        metaData
    }
    }
    """
    executed3 = gql_request(query3)
    assert isinstance(executed3, Dict)
    assert len(executed3["data"]["versions"]) == 2
    items =executed3["data"]["versions"]
    for item in items:
        if 'versionId' in item:
            item["versionId"] = int(item["versionId"])
            assert_positive_get(item)
        assert item["versionName"] == "test name B"

    # filter with abbr and versionTag
    query4 = """
            {
    versions(versionAbbreviation:"AAA",versionTag:"2"){
        versionId
        versionAbbreviation
        versionName
        versionTag
        metaData
    }
    }
    """
    executed4 = gql_request(query4)
    assert isinstance(executed4, Dict)
    items =executed4["data"]["versions"]
    print(items)
    for item in items:
        if 'versionId' in item:
            item["versionId"] = int(item["versionId"])
            assert_positive_get(item)
        assert item["versionAbbreviation"] == "AAA"
        assert item["versionTag"] ==  "2"

    variables3 = {
    "object": {
       'versionAbbreviation': "CCC",
        'versionName': 'test name C',
        'metaData': "{\"owner\":\"myself\"}"
    }
    }
    check_post(GLOBAL_QUERY,variables3)

    # check for metaData and default value for metadata
    query5 = """
            {
    versions(versionAbbreviation:"CCC"){
        versionId
        versionAbbreviation
        versionName
        versionTag
        metaData
    }
    }
    """
    headers_auth['App'] = schema_auth.App.API.value
    headers_auth['Authorization'] = "Bearer "+initial_test_users['APIUser']['token']
    executed5 = gql_request(query5,headers=headers_auth)
    assert isinstance(executed5, Dict)
    assert len(executed5["data"]["versions"]) == 1
    items =executed5["data"]["versions"]
    for item in items:
        if 'versionId' in item:
            item["versionId"] = int(item["versionId"])
            assert_positive_get(item)
        assert item["versionAbbreviation"] == "CCC"
        assert item["versionTag"] == "1"
        assert item['metaData']['owner'] == "myself"

def test_put_versions():
    """test for put versions"""
    #create version
    variables = {
    "object": {
       'versionAbbreviation': "AAA",
        'versionName': 'test name A',
        'versionTag': "1"
    }
    }
    executed = check_post(GLOBAL_QUERY,variables)
    item =executed["data"]["addVersion"]["data"]
    versionId = int(item["versionId"])

    up_query = """
    mutation editversion($object:InputEditVersion){
    editVersion(versionArg:$object){
        message
        data{
        versionId
        versionAbbreviation
        versionName
        versionTag
        metaData
        }
    }
    }
    """
    up_var = {
    "object": {
        "versionId" : versionId,
        "versionAbbreviation": "AAA",
        "versionName": "AAA version to test edited"
    }
    }

    executed = gql_request(query=up_query,operation="mutation", variables=up_var,
    headers=headers_auth)
    assert isinstance(executed, Dict)
    assert executed["data"]["editVersion"]["message"] == "Version edited successfully"
    item =executed["data"]["editVersion"]["data"]
    assert item['versionName'] == up_var["object"]['versionName']

    #edit with not owner
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    executed = gql_request(query=up_query,operation="mutation", variables=up_var,
    headers=headers_auth)
    assert "errors" in executed.keys()