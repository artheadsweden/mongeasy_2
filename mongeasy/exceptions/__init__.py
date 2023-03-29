class MongEasyException(Exception):
    pass

class MongEasyConnectionError(MongEasyException):
    pass

class MongEasyDatabaseError(MongEasyException):
    pass

class MongEasyDBCollectionError(MongEasyException):
    pass

class MongEasyDBDocumentError(MongEasyException):
    pass

class MongEasyFieldError(MongEasyException):
    pass

class MondgEasyDBInvalidDocumentError(MongEasyException):
    pass

class MongEasyIndexException(MongEasyException):
    pass