
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import StoreSchema

from db import db
from models import StoreModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

blp = Blueprint("stores", __name__, description="Store operations")


@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
            # try:
            #     return stores[store_id]
            # except KeyError:
            #     abort(404, message="Store couldn't found")

        store = StoreModel.query.get_or_404(store_id)
        return store
    
    def delete(self, store_id):
            # try:
            #     del stores[store_id]
            #     return {"message": "Store deleted."}
            # except KeyError:
            #     abort(404, message="Store couldn't found.")
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted."}, 200

@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()
    
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError():
            abort(400, message = "A store with that name already exists.")
        except SQLAlchemyError():
            abort(500, message = "An error occurred while creating the store.")
        
        return store
       
            # for store in stores.values():
            #     if store_data["name"] == store["name"]:
            #         abort(400, message=f"Store already exists.")

            # store_id = uuid.uuid4().hex
            # store = {**store_data, "id": store_id}
            # stores[store_id] = store
            # # 201 is the status code for CREATED, it means okey we get the value and we will create the store
            # return store, 201
