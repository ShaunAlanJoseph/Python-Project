from typing import Dict, Any, List, Self, Optional
from codeforces.api import user_status


class Submission:
    @classmethod
    def get_rating_changes(cls, handle: str) -> List[Self]:
        submissions = user_status(handle, count=1000)
        return [cls(data) for data in submissions]
    
    def __init__(self, data: Dict[str, Any]):
        self.id: int = data["id"]
        self.contest_id: Optional[int] = data.get("contestId", None)
        self.creationTimeSeconds: int = data["creationTimeSeconds"]
        self.relativeTimeSeconds: int = data["relativeTimeSeconds"]
        self.problem = data["problem"]
        self.author = data["author"]
        self.programmingLanguage: str = data["programmingLanguage"]
        self.verdict = data["verdict"]
        self.testset = data["testset"]
        self.passedTestCount: int = data["passedTestCount"]
        self.timeConsumedMillis: int = data["timeConsumedMillis"]
        self.memoryConsumedBytes: int = data["memoryConsumedBytes"]
        self.points: Optional[float] = data.get("points", None)
