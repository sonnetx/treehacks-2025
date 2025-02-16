from flask import Flask, jsonify
from report import ReportData, Report
from basic_pipeline import EmissionsResponse, TrashAnalyzer
from analyze_trash import CameraCapture
from dotenv import load_dotenv

import os


app = Flask(__name__)

@app.route('/api/data')
def get_data():
    
    
    # Load environment variables
    load_dotenv()
    
    # Initialize API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not openai_api_key or not perplexity_api_key:
        print("Error: Missing API keys in .env file")
        return
    
    # Initialize camera and analyzer
    camera = CameraCapture()
    analyzer = TrashAnalyzer(openai_api_key, perplexity_api_key)

    report_data = analyzer.analyze_trash(before_path, after_path)

    report = Report(report_data=report_data)
    return jsonify(report.to_dict())  # Send as JSON

if __name__ == '__main__':
    app.run(debug=True)
