import inspect
from mongeasy.models.document import Document
from mongeasy.tools.naming import pascal_to_snake
from typing import Tuple

def create_document_class(class_name: str, collection_name: str = None, base_classes: Tuple = ()) -> Document:
    """
    Dynamically create a document class and register it in the calling module's namespace.
    Args:
        class_name (str): Name of the class to create.
        collection_name (str, optional): Name of the collection. Defaults to None. 
            If None, the collection name will be the snake_case version of the class name with an 's' appended.
        schema (Union[dict, BaseModel, None], optional): _description_. An optinal schema to be used. 
            This can either be in Mongeasy format or Pydantic.  Defaults to None.
            If None this docuemnt will be schemaless.
        base_classes (tuple, optional): Optional base classes to be added to the document class. Defaults to ().

    Returns:
        _type_: The newly created document class.
    """
    # Get the calling module
    frame = inspect.currentframe().f_back
    calling_module = inspect.getmodule(frame)

    # Dynamically generate the document class
    from mongeasy import connection
    if collection_name is None:
        collection_name = pascal_to_snake(class_name) + 's'
    
    # Create the collection object
    collection = connection[collection_name]

    doc_class = type(class_name, base_classes + (Document,), {'collection':collection})

    # Register the document class in the calling module's namespace
    setattr(calling_module, class_name, doc_class)

    return doc_class