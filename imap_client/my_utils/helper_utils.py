import sys



EMAIL_PATTERN = r"""([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([
-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])"""

SUBJECT_PATTERN = r'[$= \<\>;&?!|\/\[\]\(\):\s\'\"]'


def parameter_matcher_util(null_parameter, not_null_parameter):
    return null_parameter if not_null_parameter is None else not_null_parameter


""" 
Workin with results
"""

METHOD_NAME = sys._getframe


def check_result(result):
    if result.get('result'):
        return True
    else:
        return result


def if_exist_or(object_1, object_2, object_3=None):
    if object_3 is None:
        object_3 = object_1
    return object_3 if object_1 else object_2


def result_data(result):
    return result.get('data')


def result_returner(bool_, method, data):
    return {'result': bool_, 'action_type': method.f_code.co_name, 'data': data}

