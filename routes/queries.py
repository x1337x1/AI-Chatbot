from flask import Flask, request, jsonify
from pydash import get
from controllers.open_ai_controller import OpenAiManager


def queries_routes(app):
    @app.route('/normal_query', methods=['POST'])
    def query():
        data = request.get_json() 
        query = get(data, 'query') 
        namespace = get(data, 'namespace') 
        chat_history = get(data, 'chat_history')
    
        if query and namespace and chat_history:
            open_ai_manager = OpenAiManager()
            answer_query = open_ai_manager.generate_response_chain_with_history(data)
            return jsonify({"message": answer_query}), 200
        else:
            return jsonify({"message": "Missing required fields."}), 400  

def search_engine_routes(app):
    @app.route('/search_engine_query', methods=['POST'])
    def query_search_engine():
        data = request.get_json() 
        query = get(data, 'query') 
        chat_history = get(data, 'chat_history')
        tenant_id = get(data, 'tenant_id')

        if query and chat_history and tenant_id:
            open_ai_manager = OpenAiManager()
            answer_query = open_ai_manager.generate_response_chain_search_engine(data)
            return jsonify({"message": answer_query}), 200
        else:
            return jsonify({"message": "Missing required fields."}), 400          