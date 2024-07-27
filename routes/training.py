from flask import Flask, request, jsonify
from pydash import get
from controllers.pinecone_controller import PineconeManager


def training_routes(app):
    @app.route('/train/website', methods=['POST'])
    def train_by_website():
        data = request.get_json() 
        website = get(data, 'website') 
        data_type = get(data, 'data_type') 
        namespace = get(data, 'namespace')  
    
        if website and data_type and namespace:
            pinecone_manager = PineconeManager()
            embbed_vectors = pinecone_manager.embbed_vectors(website, data_type, namespace)
            return jsonify({"message": "AI was trained successfully."}), 200  
        else:
            return jsonify({"message": "Missing required fields."}), 400  

    