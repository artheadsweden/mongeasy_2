from ctypes import Union
from typing import Any, Dict, List, Optional, Tuple, Union
from copy import copy
import datetime
import json
import logging

import bson
import pymongo

from mongeasy.exceptions import MongEasyDBCollectionError, MongEasyDBDocumentError, MongEasyFieldError
from mongeasy.models.resultlist import ResultList
from mongeasy.tools.naming import pascal_to_snake


logger = logging.getLogger(__name__)

class _DocumentBase:
    """
    Base class for all document classes.
    """
    collection = None
    def __init__(self, *args, **kwargs):
        """
        Initialize the document object.
        """
        if self.__class__.collection is None:
            from mongeasy import connection
            # Create the collection object
            collection_name = pascal_to_snake(self.__class__.__name__) + 's'            
            self.__class__.collection = connection[collection_name]

        # Handle positional arguments
        if len(args) == 1 and isinstance(args[0], dict):
            as_dict = copy(args[0])
        elif len(args) == 1 and isinstance(args[0], self.__class__):
            as_dict = copy(args[0].to_dict())
        elif len(args) == 0:
            as_dict = copy(kwargs)
        else:
            raise ValueError(f'Document() takes 1 positional argument or keyword arguments but {len(args) + len(kwargs)} were given')

        # If _id is not present we add the _id attribute
        if '_id' not in as_dict:
            self.__dict__['_id'] = None
        else:
            try:
                self._id = bson.ObjectId(str(as_dict['_id']))
            except bson.errors.InvalidId:
                raise MongEasyFieldError(f'Invalid _id: {as_dict["_id"]}')

        # Update the object
        self.__dict__.update(as_dict)
    
    def __repr__(self):
        return f'{self.__class__.__name__}({", ".join(f"{k}={v}" for k, v in self.to_dict().items())})'
    
    def __str__(self):
        nl = '\n'
        return f'{nl.join(f"{k} = {v}" for k, v in self.to_dict().items())}\n'
        
    def has_changed(self) -> dict:
        """
        Checks if any of the fields in this document has changed
        :return: dict, a dict with the changed fields, empty if no fields have changed
        """
        if self._id is None:
            return self.__dict__

        changed_fields = {}
        for key, value in self.__dict__.items():
            if key != '_id':
                try:
                    result = self.collection.find_one({'_id': self._id})
                except (pymongo.errors.OperationFailure, pymongo.errors.ServerSelectionTimeoutError) as e:
                    logger.error(f"Error querying the database: {e}")
                    return {}

                if result and key in result and result[key] != value:
                    changed_fields[key] = value
        return changed_fields
    
    def is_saved(self) -> bool:
        """
        Checks if this document has been saved to the database
        :return: bool, True if the document has been saved, False otherwise
        """
        return not bool(self.has_changed())
    
    def save(self):
        """
        Saves the current object to the database
        :return: The saved object
        """
        if self.collection is None:
            logger.error("The collection does not exist")
            raise MongEasyDBCollectionError('The collection does not exist')

       
        # If _id is None, this is a new document
        if self._id is None:
            del self._id
            res = self.collection.insert_one(self.__dict__)
            self._id = res.inserted_id
            return self

        # if no fields have changed, return the document unchanged
        if not (changed_fields := self.has_changed()):
            return self

        # update the document
        update_result = self.collection.update_one({'_id': self._id}, {'$set': changed_fields})
        if update_result.matched_count == 0:
            logger.error(f"Document with _id {self._id} does not exist")
            raise MongEasyDBDocumentError(f"Document with _id {self._id} does not exist")
        else:
            return self
    
    def reload(self):
        """
        Fetches the latest state of the document from the database and updates the current instance with the changes.
        """
        if self._id is None:
            raise MongEasyDBDocumentError('Cannot reload unsaved document')

        # fetch the latest state of the document from the database
        db_doc = self.find_one({'_id': self._id})
        if db_doc is None:
            raise MongEasyDBDocumentError(f"Document with _id {self._id} does not exist")

        # update the current instance with the changes
        for key, value in db_doc.to_dict().items():
            self.__dict__[key] = value

    def delete_field(self, field: str):
        """
        Removes a field from this document
        :param field: str, the field to remove
        :return: None
        """
        try:
            _id = self._id
            if isinstance(_id, str):
                _id = bson.ObjectId(_id)
            self.collection.update_one({'_id': _id}, {"$unset": {field: ""}})
        except Exception as e:
            logger.error(f"Error deleting field '{field}' from document with id '{self._id}': {e}")
        else:
            logger.info(f"Field '{field}' deleted from document with id '{self._id}'")

    def delete_document(self):
        """
        Delete the current object from the database
        :return: None
        """
        if self.collection is None:
            raise MongEasyDBCollectionError('The collection does not exist')

        if self._id is None:
            raise MongEasyDBDocumentError('Cannot delete unsaved document')
        _id = self._id
        if isinstance(_id, str):
            _id = bson.ObjectId(_id)
        result = self.collection.delete_one({'_id': _id})
        return result

    def to_json(self):
        """
        Serialize the document to JSON
        :return: str, the JSON representation of the document
        """
        json_dict = self.to_dict()
        return json.dumps(json_dict)
    
    def to_dict(self):
        """
        Convert the document to a dictionary.
        """
        _dict = {}
        for key, value in self.__dict__.items():
            if isinstance(value, bson.ObjectId):
                _dict[key] = str(value)
            elif isinstance(value, datetime.datetime):
                _dict[key] = value.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                _dict[key] = value
        return _dict
    
    @classmethod
    def find_raw(cls, filter_: Dict = None, projection: Union[List, Dict] = None, **kwargs) -> pymongo.cursor.Cursor:
        """
        Find documents in the database based on a filter.
        :param filter_: dict, the filter to use
        :param projection: dict or list, the projection to use
        :param kwargs: additional arguments to pass to pymongo.collection.find()
        :return: pymongo.cursor.Cursor, the cursor
        """
        if projection is None:
            projection = {}
        return cls.collection.find(filter_, projection, **kwargs)
    
    @classmethod
    def find(cls, 
             filter_dict: Dict = None, 
             projection: Union[List, Dict] = None,
             sort: Optional[Union[Tuple[str, int], List[Tuple[str, int]]]] = None, 
             limit: int = 0, 
             skip: int = 0,
             return_key: bool = False
        ) -> ResultList:
        """
        Find documents in the database based on a filter.
        
        """
        if '_id' in filter_dict and isinstance(filter_dict['_id'], str):
            filter_dict['_id'] = bson.ObjectId(filter_dict['_id'])
        query_result = cls.find_raw(filter_dict, projection, sort=sort, limit=limit, skip=skip, return_key=return_key)
        return ResultList([cls(doc) for doc in query_result])

    @classmethod
    def find_by_id(cls, _id:str) -> Union['_DocumentBase', None]:
        """
        Get a document by its _id
        :param _id: str, the id of the document
        :return: The retrieved document or None
        """
        try:
            return cls(cls.find_one({'_id': _id}))
        except bson.errors.InvalidId:
            return None
    
    @classmethod
    def find_one(cls, filter_dict=None) -> Optional['_DocumentBase']:
        """
        Get one document.
        
        :param filter_dict: A dictionary of filters.
        :return: The document or None if no document is found.
        """
        if '_id' in filter_dict and isinstance(filter_dict['_id'], bson.ObjectId):
            filter_dict = {'_id': str(filter_dict['_id'])}
        return cls.find(filter_dict, limit=1).first()
    
    @classmethod
    def find_in(cls, field, values: List) -> Optional[List[Any]]:
        """
        Get documents where the value of a field is in a list of values.
        
        :param field: The field.
        :param values: A list of values.
        :return: A list of documents or None if no documents are found.
        """
        return ResultList(cls(item) for item in cls.collection.find({field: {"$in": values}}))

    
    @classmethod
    def all(cls, 
            projection: Union[List, Dict] = None,
            sort: Optional[Union[Tuple[str, int], List[Tuple[str, int]]]] = None, 
            limit: int = 0, 
            skip: int = 0,
            return_key: bool = False
            ) -> Optional[ResultList['_DocumentBase']]:
        """
        Get all documents.
        
        :return: A list of documents or None if no documents are found.
        """
        return ResultList(cls(item) for item in cls.collection.find(projection=projection, sort=sort, limit=limit, skip=skip, return_key=return_key))
    
    @classmethod
    def delete(cls, filter_dict=None):
        """
        Delete documents.
        
        :param filter_dict: A dictionary of filters.
        """
        cls.collection.delete_many(filter_dict)
    
    @classmethod
    def insert_many(cls, documents: List[Dict]):
        """
        Insert many documents.
        
        :param documents: A list of documents.
        """
        for item in documents:
            try:
                cls(item).save()
            except pymongo.errors.WriteError as e:
                _DocumentBase.logger.exception(f"Error inserting item: {item}. Exception: {e}")
        
    
    @classmethod
    def document_count(cls, filter_dict=None) -> int:
        """
        Get the number of documents.
        
        :param filter_dict: A dictionary of filters.
        :return: The number of documents.
        """
        if filter_dict is None:
            filter_dict = {}
        return cls.collection.count_documents(filter_dict)
    
class Document(_DocumentBase):
    """
    Base document class to use with schemaless documents.
    """
    pass
    