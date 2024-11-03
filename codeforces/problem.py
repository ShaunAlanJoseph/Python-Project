from typing import Any, Dict, List, Optional, Tuple
from codeforces.api import problemset_problems
from utils.discord import BaseEmbed


class Problem:
    def __init__(self, data: Dict[str, Any]):
        self.contestId: Optional[int] = data.get("contestId", None)
        self.problemsetName: Optional[str] = data.get("problemsetName", None)
        self.index: str = data["index"]
        self.name: str = data["name"]
        self.type = data["type"]
        self.rating: Optional[int] = data.get("rating", None)
        self.tags: List[str] = data["tags"]
    
    def get_problem_embed(self) -> BaseEmbed:
        embed = BaseEmbed(title=f"{self.index}. {self.name}")
        embed.url = f"https://codeforces.com/problemset/problem/{self.contestId}/{self.index}"
        embed.add_field(name="Contest ID", value=f"{self.contestId}")
        embed.add_field(name="Rating", value=f"{self.rating}")
        embed.add_field(name="Tags", value=", ".join(self.tags))
        return embed


class ProblemStatistics:
    def __init__(self, data: Dict[str, Any]):
        self.contestId: Optional[int] = data.get("contestId", None)
        self.index: str = data["index"]
        self.solvedCount: int = data["solvedCount"]


def get_problems() -> Tuple[List[Problem], List[ProblemStatistics]]:
    problems_data, problems_stats_data = problemset_problems()
    problems = [Problem(problem) for problem in problems_data]
    problems_stats = [ProblemStatistics(stats) for stats in problems_stats_data]
    return problems, problems_stats