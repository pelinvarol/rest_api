from db import db


class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),  unique=True, nullable=False)

    items = db.relationship(
        "ItemModel", back_populates="store", lazy="dynamic", cascade="all,delete")
    
    tags = db.relationship(
        "TagModel", back_populates="store", lazy="dynamic")
    
    # lazy dynamic  just means that the items here are not going to be fetched
    # from the database until we tell it to. It's not gonna prefetch them.
    # By using lazy equal dynamic it won't do that until you tell it to, so it can speed your application up slightly at the
    # cost of having to make this request to the database later on if you wanted to. So it just gives you a bit of flexibility.


# Without lazy="dynamic", the items attribute of the StoreModel resolves to a list of ItemModel objects.

# With lazy="dynamic", the items attribute resolves to a SQLAlchemy query, which has some benefits and drawbacks:

    # A key benefit is load speed. Because SQLAlchemy doesn't have to go to the items table and load items, stores will load faster.
    # A key drawback is accessing the items of a store isn't as easy.
    # However this has another hidden benefit, which is that when you do load items, you can do things like filtering before loading.

# Here's how you could get all the items, giving you a list of ItemModel objects. Assume store is a StoreModel instance:
# store.items.all()

# And here's how you would do some filtering:
# store.items.filter_by(name=="Chair").first()
