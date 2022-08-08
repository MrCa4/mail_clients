import logging


#You should only put decorator
#@class_decorator_method(log_and_error_handler_decorator_maker)
# on class

def log_and_error_handler_decorator_maker(func, action_type: str) -> dict:
    def wrapper(self, *args, **kwargs) -> object:
        try:
            result = func(self, *args, **kwargs)
        except self.error_object as err:
            error_msg = {'result': False, 'action_type': action_type, 'error': str(err)}
            logging.error(error_msg)
            return error_msg
        except self.warning_object as warning:
            warning_msg = {'result': False, 'action_type': action_type, 'error': str(warning)}
            logging.warning(warning_msg)
            return warning_msg
        except Exception as unhandled_exception:
            critical_msg = {'result': False, 'action_type': action_type, 'error': str(unhandled_exception)}
            logging.error(critical_msg)
            return critical_msg
        else:
             try:
                 logging.info(str(result)[:1000] + "...")
             except Exception as exp:
                logging.info(str(result.get('result')+result.get('action_type')) + "...")
             return result
    return wrapper


def class_decorator_method(decorator) -> object:
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)) and not attr.startswith('__'):
                setattr(cls, attr, decorator(getattr(cls, attr), attr))
        return cls

    return decorate
