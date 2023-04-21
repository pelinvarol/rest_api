from marshmallow import Schema, fields

# The id field is a string, but it has the dump_only=True argument. This means that when we use marshmallow to validate incoming data,
# the id field won't be used or expected. However, when we use marshmallow to serialize data to be returned to a client,
# the id field will be included in the output.

# The other fields will be used for both validation and serialization, and since they have the required=True argument,
# that means that when we do validation if the fields are not present, an error will be raised.

# OLD ITEMSCHEMA, BEFORE WE REORGANİZED AS PLAINITEMSCHEMA AND ITEMSCHEMA
# class ItemSchema(Schema):
#     id = fields.Str(dump_only=True)
#     name = fields.Str(required=True)
#     price = fields.Float(required=True)
#     store_id = fields.Str(required=True)

# This is the schema for the update endpoint, which is different from the create endpoint
# because we don't need to require the name and price fields. We only need to require the
# fields that we want to update.


class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()
    # bunu eklemezsek item update ederken store_id olmadığı için sıkıntı yaşarız.
    store_id = fields.Int()
    # çünkü ItemModel yaratırken store_id zorunlu bir argüman olarak verilmişti. nullable=False değeri vardı.


class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

# And what this is gonna do is whenever we use ItemSchema, we're gonna be able to pass in the store_id when we're receiving
# data from the client. And we're also gonna have a nested store, which is fields PlainStoreSchema(), dump_only=True.
# This here will only be used when returning data to the client and not when receiving data from them.


class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)


class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    ## !!! load_only=True is so important. You never want to return the user's password when your API is returning information
    # about the user. So make sure that the password is never being sent to the client. 