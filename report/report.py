class ReportData:
    def __init__(self, 
                 numTrash: int, 
                 numCompost: int, 
                 numRecycle: int, 
                 trashNames: list[str],
                 recycleNames: list[str], 
                 compostNames: list[str], 
                 trashEmissions: float,
                 compostInTrashEmissions: float,
                 recycleInTrashEmissions: float):
        self.numTrash = numTrash
        self.numCompost = numCompost
        self.numRecycle = numRecycle
        self.trashNames = trashNames
        self.recycleNames = recycleNames
        self.compostNames = compostNames
        self.trashEmissions = trashEmissions  # Scope 2 emissions from trash in trash
        self.compostInTrashEmissions = compostInTrashEmissions  # Scope 2 emissions from compost in trash
        self.recycleInTrashEmissions = recycleInTrashEmissions  # Scope 2 emissions from recyclables in trash

    def to_dict(self):
        return {
            "numTrash": self.numTrash,
            "numCompost": self.numCompost,
            "numRecycle": self.numRecycle,
            "trashNames": self.trashNames,
            "recycleNames": self.recycleNames,
            "compostNames": self.compostNames,
            "trashEmissions": self.trashEmissions,
            "compostInTrashEmissions": self.compostInTrashEmissions,
            "recycleInTrashEmissions": self.recycleInTrashEmissions
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
