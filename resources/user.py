from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, create_refresh_token, get_jwt_identity
from blocklist import BLOCKLIST

from models import UserModel
from db import db
from schemas import UserSchema
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("Users", "users", description="User operations")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="A user with that username already exists.") 

        user = UserModel(
            username=user_data["username"],
            password=sha256.hash(user_data["password"])
        )

        db.session.add(user)
        db.session.commit()

        # the_user = UserModel.query.get_or_404(id)
        # return the_user

        return {"message": "User created successfully."}, 201
    
@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first()

        # if user with that username exist, check the correctness of password. If it is correct, return access token
        if user and sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {"message": "Logged in as {}".format(user.username), "access_token": access_token, "refresh_token": refresh_token}
        abort(401, message="Invalid username or password.")


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity() # this returns None if there is no identity in the JWT as a current user
        new_token = create_access_token(identity=current_user, fresh=False) # fresh=False ! Otherwise, a token refresh
# can be used to get fresh tokens and you don't want that.
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token": new_token}, 200
    
@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out."}

@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    @jwt_required(fresh=True)
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200