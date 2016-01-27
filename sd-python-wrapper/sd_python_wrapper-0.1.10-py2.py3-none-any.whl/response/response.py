import collections


class Response(dict):
    '''
    Simple data structure that convert any dict to an empty object
    where all the atributes are the keys of the dict, but also preserve a dict
    behavior
    e.g:
    obj = ResponseObject({'a':'b'})
    obj.key = 'value'
    obj.a   => 'b'
    obj     => {'a': 'b', 'key': 'value'}
    '''

    def __init__(self, *args, **kwargs):
        super(Response, self).__init__(*args, **kwargs)
        # print(self._methods)
        self.__dict__ = self._check_for_inception(self)
        # self._methods = [method for method in dir(self)
        #                  if not method[0] == '_']
        # self._existing_method(self)

    def _existing_method(self, dic):
        for key in dic.keys():
            if key in self._methods:
                raise ValueError('Cant set property: "{}", it is already part of Response'.format(key))

    def _check_for_inception(self, root_dict):
        '''
        Used to check if there is a dict in a dict
        '''

        for key, value in root_dict.items():
            if isinstance(value, dict):
                root_dict[key] = Response(value)

        return root_dict
