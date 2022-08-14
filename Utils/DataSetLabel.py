from __future__ import annotations

class DataSetLabel:
    """
    Data set label instance.
    """
    
    def __init__(
        self,
        groupName: str,
        startTime: float,
        endTime: float,
        startFreq: float,
        endFreq: float,
    ) -> None:
        self.groupName = groupName
        
        self.startTime: float = startTime
        self.endTime: float = endTime
        self.startFreq: float = startFreq
        self.endFreq: float = endFreq
    
    def OffsetCopy(self, offset: float) -> DataSetLabel:
        return DataSetLabel(
            self.groupName,
            self.startTime + offset,
            self.endTime + offset,
            self.startFreq,
            self.endFreq,
        )
    
    def __str__(self) -> str:
        return "{0:.2f}s->{1:.2f}s:{2:.2f}Hz->{3:.2f}Hz".format(
            self.startTime,
            self.endTime,
            self.startFreq,
            self.endFreq,
        )
    
    def ToDict(self) -> dict:
        return {
            "groupName": self.groupName,
            "startTime": self.startTime,
            "endTime": self.endTime,
            "startFreq": self.startFreq,
            "endFreq": self.endFreq,
        }