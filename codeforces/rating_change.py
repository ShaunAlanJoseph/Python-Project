from typing import Dict, Any, List, Self
from codeforces.api import user_rating


class RatingChange:
    @classmethod
    def get_rating_changes(cls, handle: str) -> List[Self]:
        rating_changes = user_rating(handle)
        return [cls(data) for data in rating_changes]
    
    def __init__(self, data: Dict[str, Any]):
        self.contestId: int = data["contestId"]
        self.contestName: str = data["contestName"]
        self.handle: str = data["handle"]
        self.rank: int = data["rank"]
        self.ratingUpdateTimeSeconds: int = data["ratingUpdateTimeSeconds"]
        self.oldRating: int = data["oldRating"]
        self.newRating: int = data["newRating"]