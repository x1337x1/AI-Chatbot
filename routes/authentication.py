from flask import Flask, request, jsonify
from pydash import get
from controllers.account_controller import Account

account = Account()


def auth_routes(app):
    @app.route('/signup', methods=['POST'])
    def signup():
        
        data = request.get_json() 
        email = get(data, 'email') 
        name = get(data, 'name') 
        password = get(data, 'password') 
    
        if email and name and password:
            register_user = account.signup(data)
            return jsonify({"message": "register was successfull"}), 200
        else:
            return jsonify({"message": "Missing email, name, or password"}), 400
    
    @app.route('/login', methods=['POST'])
    def login():

        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
             return account.login(data)
        else:
             return jsonify({"message": "Missing email, name, or password"}), 400