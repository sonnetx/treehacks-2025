class ReportData:
    def __init__(self, numTrash: int, numCompost: int, numRecycle: int, recycleNames: list[str], compostNames: list[str], recycleSavings: int, compostSavings: int):
        self.numTrash = numTrash
        self.numCompost = numCompost
        self.numRecycle = numRecycle
        self.recycleNames = recycleNames
        self.compostNames = compostNames
        self.recycleSavings = recycleSavings
        self.compostSavings = compostSavings

    def to_dict(self):
        return {
            "numTrash": self.numTrash,
            "numCompost": self.numCompost,
            "numRecycle": self.numRecycle,
            "recycleNames": self.recycleNames,
            "compostNames": self.compostNames,
            "recycleSavings": self.recycleSavings,
            "compostSavings": self.compostSavings
        }

class Report:
    def __init__(self, report_data: ReportData):
        self.report_data = report_data

    def set_report(self, report: ReportData):
        self.report = report

    @property
    def get_report(self):
        return self.report

    def to_dict(self):
        return {
            "report_data": self.report_data.to_dict() if self.report_data else None
        }
