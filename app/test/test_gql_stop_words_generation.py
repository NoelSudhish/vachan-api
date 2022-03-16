'''Tests the translation APIs that do need projects available in DB'''
import time
from typing import Dict
from sqlalchemy.sql.expression import true
from dependencies import log
#pylint: disable=E0611
from . import gql_request,check_skip_limit_gql
#pylint: disable=E0401
from .conftest import initial_test_users
from .test_stop_words_generation import update_obj1,update_obj2,update_wrong_obj,\
    add_obj,sentence_list,assert_positive_get_stopwords,assert_positive_sw_out,\
        add_bible_books,add_bible_source,add_dict_source,add_version,add_tw_dict

headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json"}


QRY_JOB_STATUS = """
    query jobstatus($jobid:Int!){
  jobStatus(jobId:$jobid){
    message
    data{
      jobId
      status
      output
    }
  }
}
"""

QRY_ADD_SW = """
    mutation addsw($language:String!,$swlist:[String]){
  addStopword(languageCode:$language,swList:$swlist){
    message
    data{
      stopWord
      stopwordType
      confidence
      metaData
      active
    }
  }
}
"""
QRY_EDIT_SW = """
    mutation editsw($language:String!,$swdata:StopWordUpdateInput){
  updateStopword(languageCode:$language,swData:$swdata){
    message
    data{
      stopWord
      stopwordType
      confidence
      metaData
      active
    }
  }
}
"""
QRY_GET_SW = """
    query getsw($lan_code:String!){
  stopwords(languageCode:$lan_code){
    stopWord
    stopwordType
    confidence
    metaData
    active
  }
}
"""
QRY_GENERATE_SW = """
    mutation generatesw($sourceName:String,$lang_code:String!,$sentence:[SWGenerateInput]){
  generateStopword(sourceName:$sourceName,languageCode:$lang_code,sentenceList:$sentence){
    message
    data{
      jobId
      status
      output
    }
  }
}
"""

update_obj1 = {
        "stopWord": "उसका",
        "active": False,
        "metaData": "{\"type\": \"verb\"}"
    }
update_obj2 = {
        "stopWord": "हम",
        "active": False,
    }
update_wrong_obj =  {
        "stopWord": "prayed",
        "active": False,
        "metaData": "{\"type\": \"verb\"}"
    }
add_obj = [
  "asd",
  "ert",
  "okl"
]

def test_get_default():
    '''positive test case, without optional params'''
    var = {
        "lan_code": "hi"
    }
    executed = gql_request(QRY_GET_SW,headers=headers_auth,variables=var)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["stopwords"])>=0
    assert isinstance(executed["data"]["stopwords"], list)

    query_check = """
        query getsw($skip:Int, $limit:Int){
  stopwords(languageCode:"hi",skip:$skip,limit:$limit){
    stopWord
    stopwordType
  }
}
    """
    check_skip_limit_gql(query_check,"stopwords")

def test_get_stop_words():
    '''Positve tests for get stopwords API'''
    var = {
        "lan_code": "hi"
    }
    executed = gql_request(QRY_GET_SW,headers=headers_auth,variables=var)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["stopwords"])>=0
    for item in executed["data"]["stopwords"]:
        assert_positive_get_stopwords(item)

    QRY_GET_SW_flags = """
           query getsw($lan_code:String!,$sys_def:Boolean){
  stopwords(languageCode:$lan_code,includeSystemDefined:$sys_def){
    stopWord
    stopwordType
    confidence
  }
}
    """
    var_flag = {"lan_code": "hi","sys_def": False}
    executed = gql_request(QRY_GET_SW_flags,headers=headers_auth,variables=var_flag)
    assert len(executed["data"]["stopwords"])>=0
    sw_types = {sw_dic['stopwordType'] for sw_dic in executed["data"]["stopwords"]}
    assert "system defined" not in sw_types

    QRY_GET_SW_flags = """
              query getsw($lan_code:String!,$usr_def:Boolean){
    stopwords(languageCode:$lan_code,includeUserDefined:$usr_def){
    stopWord
    stopwordType
    confidence
  }
}

    """
    var_flag = {"lan_code": "hi","usr_def": False}
    executed = gql_request(QRY_GET_SW_flags,headers=headers_auth,variables=var_flag)
    assert len(executed["data"]["stopwords"])>=0
    sw_types = {sw_dic['stopwordType'] for sw_dic in executed["data"]["stopwords"]}
    assert "user defined" not in sw_types

    QRY_GET_SW_flags = """
                 query getsw($lan_code:String!,$auto_def:Boolean){
  stopwords(languageCode:$lan_code,includeAutoGenerated:$auto_def){
    stopWord
    stopwordType
    confidence
  }
}
    """
    var_flag = {"lan_code": "hi","auto_def": False}
    executed = gql_request(QRY_GET_SW_flags,headers=headers_auth,variables=var_flag)
    assert len(executed["data"]["stopwords"])>0
    sw_types = {sw_dic['stopwordType'] for sw_dic in executed["data"]["stopwords"]}
    assert "auto generated" not in sw_types

    QRY_GET_SW_flags = """
                 query getsw($lan_code:String!,$active_def:Boolean){
  stopwords(languageCode:$lan_code,includeAutoGenerated:$active_def){
    stopWord
    stopwordType
    confidence
  }
}
    """
    var_flag = {"lan_code": "hi","active_def": True}
    executed = gql_request(QRY_GET_SW_flags,headers=headers_auth,variables=var_flag)
    assert len(executed["data"]["stopwords"])>0
    sw_types = {sw_dic['stopwordType'] for sw_dic in executed["data"]["stopwords"]}
    assert False not in sw_types

def test_get_notavailable_code():
    ''' request a not available language_code'''
    var = {
        "lan_code": "abc"
    }
    executed = gql_request(QRY_GET_SW,headers=headers_auth,variables=var)
    assert len(executed["data"]["stopwords"]) == 0

def test_update_stopword():
    '''Positve tests for update stopwords API'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']

    up_var = {
  "language": "hi",
  "swdata": update_obj1
}
    executed = gql_request(QRY_EDIT_SW,headers=headers_auth,variables=up_var)
    assert isinstance(executed, Dict)
    assert executed["data"]["updateStopword"]["message"]=="Stopword info updated successfully"
    assert_positive_get_stopwords(executed["data"]["updateStopword"]["data"])

    up_var2 = {
  "language": "hi",
  "swdata": update_obj2
}
    executed = gql_request(QRY_EDIT_SW,headers=headers_auth,variables=up_var2)
    assert isinstance(executed, Dict)
    assert executed["data"]["updateStopword"]["message"]=="Stopword info updated successfully"
    assert_positive_get_stopwords(executed["data"]["updateStopword"]["data"])

    up_var_wrong = {
  "language": "hi",
  "swdata": update_wrong_obj
}
    executed = gql_request(QRY_EDIT_SW,headers=headers_auth,variables=up_var_wrong)
    assert isinstance(executed, Dict)
    assert 'errors' in executed

def test_add_stopword():
    '''Positve tests for add stopwords API'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']

    add_var = {
  "language": "aa",
  "swlist": add_obj
}
    executed = gql_request(QRY_ADD_SW,headers=headers_auth,variables=add_var)
    assert 'message' in executed["data"]["addStopword"]
    assert 'data' in executed["data"]["addStopword"]
    for item in executed["data"]["addStopword"]['data']:
        assert_positive_get_stopwords(item)
        assert item['stopwordType'] == "user defined"
        assert item['active'] is True
        assert item['stopWord'] in add_obj
    assert len(executed["data"]["addStopword"]['data']) == len(add_obj)

    add_var = {
  "language": "aa",
  "swlist": ["asd"]
}
    executed = gql_request(QRY_ADD_SW,headers=headers_auth,variables=add_var)
    assert executed["data"]["addStopword"]["message"] == "0 stopwords added successfully"
    assert len(executed["data"]["addStopword"]["data"]) == 0

    add_var = {
  "language": "aa",
  "swlist": ["hty"]
}
    executed = gql_request(QRY_ADD_SW,headers=headers_auth,variables=add_var)
    assert executed["data"]["addStopword"]["message"] == "1 stopwords added successfully"
    assert len(executed["data"]["addStopword"]["data"]) == 1
    assert executed["data"]["addStopword"]["data"][0]['stopWord'] == "hty"
    assert executed["data"]["addStopword"]["data"][0]['stopwordType'] == "user defined"
    assert executed["data"]["addStopword"]["data"][0]['active'] is True
    assert len(executed["data"]["addStopword"]["data"]) == 1

    add_var = {
  "language": "hi",
  "swlist": ["चुनाव"]
}
    executed = gql_request(QRY_ADD_SW,headers=headers_auth,variables=add_var)
    assert executed["data"]["addStopword"]["message"] == "1 stopwords added successfully"
    assert len(executed["data"]["addStopword"]["data"]) == 1
    assert executed["data"]["addStopword"]["data"][0]['stopWord'] == "चुनाव"
    assert executed["data"]["addStopword"]["data"][0]['stopwordType'] == "user defined"
    assert executed["data"]["addStopword"]["data"][0]['active'] is True
    assert len(executed["data"]["addStopword"]["data"]) == 1

def get_job_status(job_id):
    '''Retrieve status of a job'''
    var = {
  "jobid": job_id
}
    #registered user can get status
    response = gql_request(QRY_JOB_STATUS,headers=headers_auth,variables=var)
    assert "errors" in response.keys()

    response = gql_request(QRY_JOB_STATUS,headers=headers_auth,variables=var)
    assert "message" in response["data"]["jobStatus"]
    assert "data" in response["data"]["jobStatus"]
    assert "jobId" in response["data"]["jobStatus"]['data']
    assert "status" in response["data"]["jobStatus"]['data']
    return response["data"]["jobStatus"]

# def test_generate_stopwords():
#     '''Positve tests for generate stopwords API'''
#     add_version()
#     table_name = add_bible_source()
#     add_bible_books(table_name)

#     table_name = add_dict_source()
#     add_tw_dict(table_name)
#     headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']

#     var_gen = {
#   "lang_code": "hi"
# }
#     QRY_GEN = """
#         mutation generatesw($lang_code:String!){
#   generateStopword(languageCode:$lang_code){
#     message
#     data{
#       jobId
#       status
#       output
#     }
#   }
# }
#     """
#     executed = gql_request(QRY_GEN,headers=headers_auth,variables=var_gen)
#     assert "message" in executed["data"]["generateStopword"]
#     assert "data" in executed["data"]["generateStopword"]
#     assert "jobId" in executed["data"]["generateStopword"]['data']
#     assert "status" in executed["data"]["generateStopword"]['data']
#     for i in range(10):
#         job_response1 = get_job_status(executed["data"]["generateStopword"]['data']['jobId'])
#         status = job_response1['data']['status']
#         if status == 'job finished':
#             break
#         log.info(job_response1)
#         log.info("sleeping for a minute in SW generate test")
#         time.sleep(60)
#     assert job_response1['data']['status'] == 'job finished'
#     assert 'output' in job_response1['data']
#     for item in job_response1['data']['output']['data']:
#         assert_positive_sw_out(item)
#     assert job_response1['message'] == "Stopwords identified out of limited resources. Manual verification recommended"

#     var_gen2 = {
#   "sourceName": table_name,
#   "lang_code": "hi",
#   "sentence": sentence_list
# }

#     executed = gql_request(QRY_GENERATE_SW,headers=headers_auth,variables=var_gen2)
#     assert "message" in executed["data"]["generateStopword"]
#     assert "data" in executed["data"]["generateStopword"]
#     assert "jobId" in executed["data"]["generateStopword"]['data']
#     assert "status" in executed["data"]["generateStopword"]['data']
#     for i in range(10):
#         job_response2 = get_job_status(executed["data"]["generateStopword"]['data']['jobId'])
#         status = job_response2['data']['status']
#         if status == 'job finished':
#             break
#         log.info("sleeping for a minute in SW generate test")
#         time.sleep(60)
#     assert job_response2['data']['status'] == 'job finished'
#     assert 'output' in job_response2['data']
#     for item in job_response2['data']['output']['data']:
#         assert_positive_sw_out(item)
#     assert len(job_response2['data']['output']['data']) < len(job_response1
#                                                             ['data']['output']['data'])
#     assert job_response2['message'] == "Automatically generated stopwords for the given language"
