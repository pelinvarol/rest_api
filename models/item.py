from db import db

class ItemModel(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),  unique=True, nullable=False)
    price = db.Column(db.Float(precision=2), unique= False, nullable=False)

    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), unique = False, nullable=False)
    store = db.relationship("StoreModel", back_populates="items")
    tags = db.relationship("TagModel", back_populates="items",secondary="items_tags")
    
    # SQLAlchemy knows that the stores table is used by the StoreModel class.
    # So when we have a store ID that is using the stores table, we can then define a
    # relationship with the StoreModel class, and it will automatically populate the
    # store variable with a StoreModel object, whose ID matches that of the foreign key.
    # This is pretty handy because it will mean that when we have an ItemModel
    # object, we can just say my_item.store, and that will be a StoreModel object
    # that is associated with the item.

    # Back_populates equal items is gonna be used so that the StoreModel class
    # will also have an items relationship here that allows each StoreModel
    # object to see very easily, all of the items that are associated with it.