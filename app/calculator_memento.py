from dataclasses import dataclass, field
import datetime
from typing import Any, Dict, List

from app.calculation import Calculation

@dataclass
class CalculatorMemento:

    history: List[Calculation]
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'history': [calc.to_dict() for calc in self.history],
            'timestamp': self.timestamp.isoformat()
        }
    

    # class method to convert a Calculation object to a dictionary format suitable for serialization.
    # This method is used when saving the state of the calculator's history to a file or other storage medium.
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalculatorMemento':

        return cls(
            
            # The history is reconstructed by creating Calculation instances from the list of dictionaries in the 'history' key of the input data.
            # Each dictionary is passed to the from_dict method of the Calculation class to create a Calculation object.
            history=[Calculation.from_dict(calc) for calc in data['history']],
            timestamp=datetime.datetime.fromisoformat(data['timestamp'])    
        )
