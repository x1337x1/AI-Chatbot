from flask import Flask, request, jsonify
from pydash import get
from controllers.account_controller import Account

account = Account()


def auth_routes(app):
    @app.route('/signup', methods=['POST'])
    def signup():
        
        data = request.get_json() 
        email = get(data, 'email') 
        first_name = get(data, 'first_name') 
        last_name = get(data, 'last_name') 
        password = get(data, 'password') 
        tenant_fingerprint = get(data, 'fingerprint')
        if email and first_name and last_name and tenant_fingerprint and password:
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