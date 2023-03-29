from mongeasy import BaseDocument, SubDocument
from bson import ObjectId

class Address(SubDocument):
    street: str
    city: str
    state: str
    zip: str
    
class User(BaseDocument):
    _id: ObjectId
    name: str
    age: int
    address: Address
    
    
user = User(name='Wokie', age=56, address=Address(street='123 Main St', city='Anytown', state='CA', zip='12345'))
user.save()