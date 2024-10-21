from enum import IntEnum
from datetime import datetime, timedelta

class Rating(IntEnum):

    Fail = 0
    Pass = 1

class Card:

    box: int
    due: datetime

    def __init__(self, box=1, due=None):

        self.box = box
        self.due = due

    def to_dict(self):

        return_dict = {
            "box": self.box,
        }

        if self.due is not None:

            return_dict["due"] = self.due.isoformat()

        return return_dict
    
    @staticmethod
    def from_dict(source_dict):

        box = int(source_dict['box'])

        if "due" in source_dict:

            due = datetime.fromisoformat(source_dict["due"])
        else:
            due = None

        return Card(box=box, due=due)


class ReviewLog:

    rating: int
    review_datetime: datetime
    box: int

    def __init__(self, rating, review_datetime, box):

        self.rating = rating
        self.review_datetime = review_datetime
        self.box = box

    def to_dict(self):

        return_dict = {
            "rating": self.rating.value,
            "review_datetime": self.review_datetime.isoformat(),
            "box": self.box
        }

        return return_dict
    
    @staticmethod
    def from_dict(source_dict):

        rating = Rating(int(source_dict["rating"]))
        review_datetime = datetime.fromisoformat(source_dict["review_datetime"])
        box = int(source_dict["box"])

        return ReviewLog(rating=rating, review_datetime=review_datetime, box=box)

class LeitnerScheduler:

    box_intervals: list[int]
    start_datetime: datetime
    on_fail: str

    def __init__(self, box_intervals=[1, 2, 7], start_datetime=None, on_fail='first_box'):

        self.box_intervals = box_intervals # how many days in between you review each box; default box1 - everyday, box2 - every 2 days, box3, every seven days
        if start_datetime is None:
            self.start_datetime = datetime.now()
        else:
            self.start_datetime = start_datetime

        self.on_fail = on_fail

    def review_card(self, card, rating, review_datetime=None):

        if review_datetime is None:
            review_datetime = datetime.now()

        if card.due is None:
            card.due = review_datetime.replace(hour=0, minute=0, second=0, microsecond=0) # beginning of the day of review

        card_is_due = review_datetime >= card.due
        if not card_is_due:
            raise RuntimeError(f"Card is not due for review until {card.due}.")

        review_log = ReviewLog(rating, review_datetime, card.box)

        if rating == Rating.Fail:

            if self.on_fail == 'first_box':
                card.box = 1
            elif self.on_fail == 'prev_box' and card.box > 1:
                card.box -= 1

        elif rating == Rating.Pass:

            if card.box < len(self.box_intervals):
                card.box += 1

        interval = self.box_intervals[card.box-1]

        begin_datetime = (self.start_datetime - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        i = 1
        next_due_date = begin_datetime + (timedelta(days=interval) * i)
        while next_due_date <= review_datetime:

            next_due_date = begin_datetime + (timedelta(days=interval) * i)
            i += 1

        card.due = next_due_date

        return card, review_log
    
    def to_dict(self):

        return_dict = {
            "box_intervals": self.box_intervals,
            "start_datetime": self.start_datetime.isoformat(),
            "on_fail": self.on_fail
        }

        return return_dict
    
    @staticmethod
    def from_dict(source_dict):

        box_intervals = source_dict['box_intervals']
        start_datetime = datetime.fromisoformat(source_dict['start_datetime'])
        on_fail = source_dict['on_fail']

        return LeitnerScheduler(box_intervals=box_intervals, start_datetime=start_datetime, on_fail=on_fail)