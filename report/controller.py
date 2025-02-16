from flask import Flask, jsonify
from report import ReportData, Report
from basic_pipeline import EmissionsResponse, TrashAnalyzer

import os


app = Flask(__name__)

@app.route('/api/data')
def get_data():
    
    
    # reportData = ReportData(numTrash=40, numCompost=5, numRecycle=15, recycleNames=["Plastic", "Paper"], compostNames=["Apple Core"], recycleSavings=20, compostSavings=10)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
    
    analyzer = TrashAnalyzer(openai_api_key, perplexity_api_key)
    
    before_image_path = "sample-images/notrash.jpg"
    after_image_path = "sample-images/IMG_6703.jpg"
    report_data = analyzer.analyze_trash(before_image_path, after_image_path)

    report = Report(report_data=report_data)
    return jsonify(report.to_dict())  # Send as JSON

if __name__ == '__main__':
    app.run(debug=True)
