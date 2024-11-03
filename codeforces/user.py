from datetime import datetime
from typing import Optional, List, Self, Dict, Any
from codeforces.rating_change import RatingChange
from codeforces.submission import Submission
from codeforces.api import users_info
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import numpy as np
from io import BytesIO
from utils.discord import BaseEmbed
from collections import Counter


class User:
    @classmethod
    def get_users(cls, handles: List[str]) -> List[Self]:
        users_data = users_info(handles)
        return [cls(handle, user_data) for handle, user_data in zip(handles, users_data)]
    
    def __init__(self, handle: str, user_data: Optional[Dict[str, Any]] = None):
        self.handle: str = handle

        if user_data is None:
            user_data = users_info([handle])[0]

        self.email: Optional[str] = user_data.get("email", None)
        self.firstName: Optional[str] = user_data.get("firstName", None)
        self.lastName: Optional[str] = user_data.get("lastName", None)
        self.country: Optional[str] = user_data.get("country", None)
        self.city: Optional[str] = user_data.get("city", None)
        self.organization: Optional[str] = user_data.get("organization", None)
        self.contribution: Optional[int] = user_data.get("contribution", None)
        self.rank: Optional[str] = user_data.get("rank", None)
        self.rating: Optional[int] = user_data.get("rating", None)
        self.maxRank: Optional[str] = user_data.get("maxRank", None)
        self.maxRating: Optional[int] = user_data.get("maxRating", None)
        self.lastOnlineTimeSeconds: Optional[int] = user_data.get("lastOnlineTimeSeconds", None)
        self.registrationTimeSeconds: Optional[int] = user_data.get("registrationTimeSeconds", None)
        self.friendOfCount: Optional[int] = user_data.get("friendOfCount", None)
        self.avatar: Optional[str] = user_data.get("avatar", None)
        self.titlePhoto: Optional[str] = user_data.get("titlePhoto", None)

        self.rating_changes: Optional[List[RatingChange]] = None
        self.submissions: Optional[List[Submission]] = None
    
    def load_rating_changes(self):
        self.rating_changes = RatingChange.get_rating_changes(self.handle)
    
    def load_submissions(self):
        self.submissions = Submission.get_rating_changes(self.handle)
    
    def get_user_rating_graph(self) -> BytesIO:
        return self.get_user_rating_comparison_graph([])
    
    def get_user_rating_change_graph(self) -> BytesIO:
        return self.get_user_rating_change_comparison_graph([])
    
    def get_user_rating_change_comparison_graph(self, users: List[Self]) -> BytesIO:
        if self.rating_changes is None:
            self.load_rating_changes()
        
        for user in users:
            if user.rating_changes is None:
                user.load_rating_changes()
        
        plt.figure(figsize=(12, 6))
    
        # Get rating changes for current user if not already loaded
        if self.rating_changes is None:
            self.rating_changes = RatingChange.get_rating_changes(self.handle)
        
        # Plot current user's ratings
        if self.rating_changes:
            dates = [datetime.fromtimestamp(change.ratingUpdateTimeSeconds) 
                    for change in self.rating_changes]
            ratings = [change.newRating for change in self.rating_changes]
            plt.plot(dates, ratings, marker='o', label=self.handle, linewidth=2)
        
        # Plot other users' ratings
        colors = plt.cm.tab10(np.linspace(0, 1, len(users)))
        for user, color in zip(users, colors):
            if user.handle != self.handle:  # Skip if it's the same as current user
                rating_changes = RatingChange.get_rating_changes(user.handle)
                if rating_changes:
                    dates = [datetime.fromtimestamp(change.ratingUpdateTimeSeconds) 
                            for change in rating_changes]
                    ratings = [change.newRating for change in rating_changes]
                    plt.plot(dates, ratings, marker='o', label=user.handle, 
                            linewidth=2, color=color, alpha=0.7)
        
        # Customize the plot
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Rating', fontsize=12)
        plt.title('Rating Comparison', fontsize=14, pad=20)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Format date axis
        plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
        plt.gcf().autofmt_xdate()  # Rotate and align the tick labels
        
        # Add rating ranges for different ranks
        rank_ranges = [
            (3000, float('inf'), 'red', 'Legendary Grandmaster'),
            (2600, 3000, 'red', 'International Grandmaster'),
            (2400, 2600, 'red', 'Grandmaster'),
            (2300, 2400, 'orange', 'International Master'),
            (2100, 2300, 'orange', 'Master'),
            (1900, 2100, 'violet', 'Candidate Master'),
            (1600, 1900, 'blue', 'Expert'),
            (1400, 1600, 'cyan', 'Specialist'),
            (1200, 1400, 'green', 'Pupil'),
            (-float('inf'), 1200, 'gray', 'Newbie')
        ]
        
        # Add subtle background colors for rating ranges
        for min_rating, max_rating, color, rank_name in rank_ranges:
            plt.axhspan(min_rating, max_rating, color=color, alpha=0.1)
            plt.text(plt.gca().get_xlim()[1], (min_rating + max_rating) / 2, 
                    f' {rank_name}', verticalalignment='center')
        
        # Adjust layout to prevent text cutoff
        plt.tight_layout()
        
        # Save plot to bytes buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
        buffer.seek(0)
        plt.close()
        
        return buffer
    
    def get_user_rating_comparison_graph(self, users: List[Self]) -> BytesIO:
        # Combine current user with comparison users
        all_users = [self] + [u for u in users if u.handle != self.handle]
        
        # Prepare data
        handles = [user.handle for user in all_users]
        current_ratings = [user.rating if user.rating else 0 for user in all_users]
        max_ratings = [user.maxRating if user.maxRating else 0 for user in all_users]
        
        # Set up the plot
        plt.figure(figsize=(12, 6))
        x = np.arange(len(handles))
        width = 0.35
        
        # Create bars
        current_bars = plt.bar(x - width/2, current_ratings, width, 
                            label='Current Rating', color='royalblue')
        max_bars = plt.bar(x + width/2, max_ratings, width,
                        label='Max Rating', color='lightcoral')
        
        # Customize the plot
        plt.ylabel('Rating', fontsize=12)
        plt.title('Rating Comparison', fontsize=14, pad=20)
        plt.xticks(x, handles, rotation=45, ha='right')
        plt.legend()
        
        # Add value labels on the bars
        def autolabel(bars):
            for bar in bars:
                height = bar.get_height()
                plt.annotate(f'{int(height)}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')
        
        autolabel(current_bars)
        autolabel(max_bars)
        
        # Add rating ranges for different ranks
        rank_ranges = [
            (3000, float('inf'), 'red', 'Legendary Grandmaster'),
            (2600, 3000, 'red', 'International Grandmaster'),
            (2400, 2600, 'red', 'Grandmaster'),
            (2300, 2400, 'orange', 'International Master'),
            (2100, 2300, 'orange', 'Master'),
            (1900, 2100, 'violet', 'Candidate Master'),
            (1600, 1900, 'blue', 'Expert'),
            (1400, 1600, 'cyan', 'Specialist'),
            (1200, 1400, 'green', 'Pupil'),
            (-float('inf'), 1200, 'gray', 'Newbie')
        ]
        
        # Add subtle horizontal lines for rating ranges
        for min_rating, max_rating, color, rank_name in rank_ranges:
            plt.axhline(y=min_rating, color=color, alpha=0.2, linestyle='--')
            plt.text(plt.gca().get_xlim()[1], min_rating, 
                    f' {rank_name}', verticalalignment='bottom')
        
        # Add grid
        plt.grid(True, axis='y', linestyle='--', alpha=0.3)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save plot to bytes buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
        buffer.seek(0)
        plt.close()
        
        return buffer
    
    def get_user_subs_verdict_graph(self) -> BytesIO:
        if self.submissions is None:
            self.load_submissions()
        
        assert self.submissions is not None
        # Count verdicts
        verdict_counts = Counter(sub.verdict for sub in self.submissions)
        
        # Define colors for common verdicts
        verdict_colors = {
            'OK': '#4CAF50',  # Green for Accepted
            'WRONG_ANSWER': '#F44336',  # Red for Wrong Answer
            'TIME_LIMIT_EXCEEDED': '#FFC107',  # Amber for TLE
            'MEMORY_LIMIT_EXCEEDED': '#FF9800',  # Orange for MLE
            'RUNTIME_ERROR': '#9C27B0',  # Purple for Runtime Error
            'COMPILATION_ERROR': '#795548',  # Brown for Compilation Error
            'FAILED': '#607D8B',  # Blue Grey for Failed
            'PARTIAL': '#2196F3',  # Blue for Partial
            'SKIPPED': '#9E9E9E',  # Grey for Skipped
            'CHALLENGED': '#E91E63',  # Pink for Challenged
            'REJECTED': '#F44336',  # Red for Rejected
        }
        
        # Prepare data for plotting
        labels = []
        sizes = []
        colors = []
        others = 0
        others_label = []
        
        # Sort verdicts by frequency
        for verdict, count in sorted(verdict_counts.items(), key=lambda x: x[1], reverse=True):
            # For verdicts with very small counts, group them into "Others"
            if count / len(self.submissions) < 0.01:  # Less than 1%
                others += count
                others_label.append(f"{verdict}({count})")
            else:
                labels.append(f"{verdict}\n({count})")
                sizes.append(count)
                colors.append(verdict_colors.get(verdict, '#9E9E9E'))  # Default to grey if color not defined
        
        # Add others if any
        if others > 0:
            labels.append(f"Others\n({others})\n{', '.join(others_label)}")
            sizes.append(others)
            colors.append('#9E9E9E')
        
        # Create figure
        plt.figure(figsize=(10, 8))
        
        # Create pie chart
        patches, texts, autotexts = plt.pie(sizes, 
                                        labels=labels,
                                        colors=colors,
                                        autopct='%1.1f%%',
                                        pctdistance=0.85,
                                        explode=[0.05] * len(sizes))
        
        # Add title
        plt.title('Submission Verdicts Distribution', pad=20, fontsize=14)
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        plt.axis('equal')
        
        # Add legend with number of total submissions
        plt.legend(patches, labels, 
                title=f'Total Submissions: {len(self.submissions)}',
                loc='center left',
                bbox_to_anchor=(1, 0, 0.5, 1))
        
        # Adjust layout to prevent text cutoff
        plt.tight_layout()
        
        # Save plot to bytes buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
        buffer.seek(0)
        plt.close()
        
        return buffer
    
    def get_user_details_embed(self) -> BaseEmbed:
        embed = BaseEmbed(title=f"{self.handle}'s Details")
        embed.add_field(name="Name", value=f"{self.firstName} {self.lastName}")
        embed.add_field(name="Country", value=f"{self.country}", inline=True) 
        embed.add_field(name="City", value=f"{self.city}", inline=True)
        embed.add_field(name="Organization", value=f"{self.organization}", inline=True)
        embed.add_field(name="Contribution", value=f"{self.contribution}")
        embed.add_field(name="Rank", value=f"{self.rank}", inline=True)
        embed.add_field(name="Max Rank", value=f"{self.maxRank}", inline=True)
        embed.add_field(name="")
        embed.add_field(name="Rating", value=f"{self.rating}", inline=True)
        embed.add_field(name="Max Rating", value=f"{self.maxRating}", inline=True)
        embed.add_field(name="")
        embed.add_field(name="Last Online Time", value=f"{self.lastOnlineTimeSeconds}", inline=True)
        embed.add_field(name="Registration Time", value=f"{self.registrationTimeSeconds}", inline=True)
        embed.add_field(name="")
        embed.add_field(name="Friend Of Count", value=f"{self.friendOfCount}")
        embed.set_image(url=self.avatar)
        return embed