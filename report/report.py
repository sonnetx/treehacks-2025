class ReportData:
    def __init__(self, numTrash: int, numCompost: int, numRecycle: int, recycleNames: list[str], compostNames: list[str], recycleSavings: int, compostSavings: int):
        self.numTrash = numTrash
        self.numCompost = numCompost
        self.numRecycle = numRecycle
        self.recycleNames = recycleNames
        self.compostNames = compostNames
        self.recycleSavings = recycleSavings
        self.compostSavings = compostSavings

class Report:
    def __init__(self, report_data: ReportData):
        self.report_data = report_data

    def set_report(self, report: ReportData):
        self.report = report

    @property
    def get_report(self):
        return self.report