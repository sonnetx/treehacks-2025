from flask import Flask, jsonify
from report import ReportData, Report
from ..basic_pipeline import EmissionsResponse, TrashAnalyzer


app = Flask(__name__)

@app.route('/api/data')
def get_data():
    
    
    reportData = ReportData(numTrash=40, numCompost=5, numRecycle=15, recycleNames=["Plastic", "Paper"], compostNames=["Apple Core"], recycleSavings=20, compostSavings=10)
    report = Report(report_data=reportData)
    return jsonify(report.to_dict())  # Send as JSON

if __name__ == '__main__':
    app.run(debug=True)
