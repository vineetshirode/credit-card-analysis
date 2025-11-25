from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from data_processor import CreditCardDataProcessor
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for API requests

# Initialize data processor
data_processor = CreditCardDataProcessor()

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/api/merchant-trust', methods=['POST'])
def merchant_trust():
    """API endpoint for merchant trust score"""
    try:
        data = request.get_json()
        
        # Add debug logging
        print(f"Received data: {data}")
        
        merchant_name = data.get('merchant_name', '') if data else ''
        
        print(f"Merchant name extracted: '{merchant_name}'")
        
        if not merchant_name:
            return jsonify({'error': 'Merchant name is required'}), 400
        
        result = data_processor.get_merchant_trust_score(merchant_name)
        
        if result is None:
            return jsonify({'error': 'Merchant not found'}), 404
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error in merchant_trust endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/customer-analysis', methods=['POST'])
def customer_analysis():
    """API endpoint for customer analysis"""
    try:
        data = request.get_json()
        customer_id = data.get('customer_id', '')
        
        if not customer_id:
            return jsonify({'error': 'Customer ID is required'}), 400
        
        result = data_processor.get_customer_analysis(customer_id)
        
        if result is None:
            return jsonify({'error': 'Customer not found'}), 404
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/category-insights', methods=['POST'])
def category_insights():
    """API endpoint for category insights"""
    try:
        data = request.get_json()
        category = data.get('category', '')
        
        if not category:
            return jsonify({'error': 'Category is required'}), 400
        
        result = data_processor.get_category_insights(category)
        
        if result is None:
            return jsonify({'error': 'Category not found'}), 404
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/risk-assessment', methods=['POST'])
def risk_assessment():
    """API endpoint for transaction risk assessment"""
    try:
        data = request.get_json()
        amount = data.get('amount', 0)
        category = data.get('category', '')
        
        if not amount or not category:
            return jsonify({'error': 'Amount and category are required'}), 400
        
        result = data_processor.assess_transaction_risk(float(amount), category)
        
        if result is None:
            return jsonify({'error': 'Unable to assess risk'}), 404
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/city-analysis', methods=['POST'])
def city_analysis():
    """API endpoint for city analysis"""
    try:
        data = request.get_json()
        city_name = data.get('city_name', '')
        
        if not city_name:
            return jsonify({'error': 'City name is required'}), 400
        
        result = data_processor.get_city_analysis(city_name)
        
        if result is None:
            return jsonify({'error': 'City not found'}), 404
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/spending-prediction', methods=['POST'])
def spending_prediction():
    """API endpoint for spending prediction"""
    try:
        data = request.get_json()
        age = data.get('age', 0)
        gender = data.get('gender', 'M')
        
        if not age:
            return jsonify({'error': 'Age is required'}), 400
        
        result = data_processor.predict_spending(int(age), gender)
        
        if result is None:
            return jsonify({'error': 'Unable to predict'}), 404
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard-stats', methods=['GET'])
def dashboard_stats():
    """API endpoint for dashboard statistics"""
    try:
        result = data_processor.get_dashboard_stats()
        
        if result is None:
            return jsonify({'error': 'Unable to fetch statistics'}), 500
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Credit Card Analysis API is running',
        'data_loaded': data_processor.df is not None
    }), 200

if __name__ == '__main__':
    print("="*60)
    print("🚀 Starting Credit Card Analysis Dashboard")
    print("="*60)
    print(f"📊 Dataset: {data_processor.data_path}")
    print(f"📈 Records loaded: {len(data_processor.df) if data_processor.df is not None else 0}")
    print("="*60)
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("="*60)
    
    # Run the Flask app
    # For local: debug=True
    # For production: debug=False
    app.run(debug=False, host='0.0.0.0', port=5000)