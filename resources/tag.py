from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import TagModel, StoreModel, ItemModel
from schemas import TagSchema, TagAndItemSchema

blp = Blueprint("tags", __name__, description="Tag operations")


@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView): # store can have many tags

    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()
    
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        if TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first():
            abort(400, message="Tag with name '{}' already exists in store '{}'.".format(tag_data["name"], store_id))
                  
        #Schema may have a store ID or it may not and it will also have ID and name.So when we get the store_id through the URL, 
        # we're gonna use that instead of relying on the tag data.
        tag = TagModel(**tag_data, store_id=store_id)

        try: 
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return tag

@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(201, TagSchema())
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        # make sure that you can only link a tag that belongs to a certain store, with an item of that same store.
        if item.store.id != tag.store.id:
             abort(400, message="Make sure item and tag belong to the same store before linking.")

        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while linking the tag to the item.")
        
        return tag
    
    @blp.response(200, TagAndItemSchema())
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        # make sure that you can only link a tag that belongs to a certain store, with an item of that same store.
        if item.store.id != tag.store.id:
             abort(400, message="Make sure item and tag belong to the same store before deleting.")
        
        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while unlinking the tag.")

        return {"message": "Tag unlinked from item.", "item": item, "tag": tag}


@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    

    @blp.response(
        202,
        description="Deletes a tag if no item is tagged with it.",
        example={"message": "Tag deleted."},
    )
    @blp.alt_response(404, description="Tag not found.")
    @blp.alt_response(
        400,
        description="Returned if the tag is assigned to one or more items. In this case, the tag is not deleted.",
    )
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message":"Tag deleted."}
        abort(400, message="Tag cannot be deleted. Make sure tag is not associated with any items, then try again.")

