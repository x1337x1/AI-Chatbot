from flask import Flask, request, jsonify
from pydash import get
from controllers.open_ai_controller import OpenAiManager


def queries_routes(app):
    @app.route('/query', methods=['POST'])
    def query():
        data = request.get_json() 
        query = get(data, 'query') 
        namespace = get(data, 'namespace') 
        chat_history = get(data, 'chat_history')
    
        if query and namespace:
            open_ai_manager = OpenAiManager()
            answer_query = open_ai_manager.generate_response_chain_with_history(query, namespace, chat_history)
            return jsonify({"message": answer_query}), 200
        else:
            return jsonify({"message": "Missing required fields."}), 400  
        