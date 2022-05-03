from app.main.func import db_request, db_filter_req, get_active_staff_id, get_data
from app.schedule.func import get_lessons, get_disc_list
from config import ApeksConfig as Apeks


class ApeksStaffData:
    def __init__(self):
        self.active_staff_id = get_active_staff_id()
        self.data = get_data(self.active_staff_id)
        self.staff = self.data["staff"]
        self.departments = self.data["departments"]

    def get_staff(self, department_id):
        """Getting staff ID and sorting them by position at the department."""

        def staff_sort(staff_id):
            """Getting sorting code by position."""
            position_id = ""
            for history in state_staff_history:
                if history.get("staff_id") == str(staff_id):
                    if history.get("position_id") in Apeks.EXCLUDE_LIST:
                        return None
                    else:
                        position_id = history.get("position_id")
            for k in state_staff_positions:
                if k.get("id") == position_id:
                    return k.get("sort")

        state_staff_positions = db_request("state_staff_positions")
        state_staff_history = db_filter_req(
            "state_staff_history", "department_id", department_id
        )
        sort_dict = {}
        for i in self.staff[str(department_id)].keys():
            staff_sort_val = staff_sort(i)
            if staff_sort_val:
                sort_dict[i] = int(staff_sort_val)
        a = sorted(sort_dict.items(), key=lambda x: x[1], reverse=True)
        prepod_dict = {}
        for i in range(len(a)):
            prepod_dict[a[i][0]] = self.staff_name(a[i][0], department_id)
        return prepod_dict

    def staff_name(self, staff_id, department_id):
        """Short staff name without rank."""
        if self.staff[str(department_id)][str(staff_id)]["specialRank"] is None:
            return self.staff[str(department_id)][str(staff_id)]["shortName"]
        else:
            rank_name = self.staff[str(department_id)][str(staff_id)]["specialRank"][
                "name_short"
            ]
            return self.staff[str(department_id)][str(staff_id)]["shortName"].replace(
                rank_name + " ", ""
            )


class ApeksLessons:
    def __init__(self, staff_id, month, year):
        self.data = get_lessons(staff_id, month, year)
        self.plan_disciplines = get_disc_list()

    def calendar_name(self, lesson):
        """Combined topic + discipline name for calendar."""
        class_type_name = self.data[lesson]["class_type_name"]
        text = (
            class_type_name
            + self.topic_code(lesson)
            + self.short_disc_name(self.data[lesson]["discipline_id"])
            + " "
            + self.data[lesson]["groupName"]
        )
        return text

    def time_start_xlsx(self, lesson) -> str:
        """Time start lesson for xlsx."""
        time = self.data[lesson]["lessonTime"].split(" - ")
        fulltime = f"{self.data[lesson]['date']} {time[0]}"
        return fulltime

    def time_ical(self, pos, lesson):
        """
        Время начала/конца занятия для формата iCal
        pos in ['start', 'end']
        """
        i = 0 if pos == 'start' else 1 if pos == 'end' else None
        date = self.data[lesson]["date"].split(".")
        time = self.data[lesson]["lessonTime"].split(" - ")[i]
        utf_fix = str(int(time.split(":")[0]) - Apeks.TIMEZONE)
        if len(utf_fix) < 2:
            utf_fix = f"0{utf_fix}"
        return f"{date[2]}{date[1]}{date[0]}T{utf_fix}{time.split(':')[1]}00Z"

    def topic_name(self, lesson):
        """Get topic name."""
        if self.data[lesson]["topic_name"] is None:
            name = " "
        else:
            name = self.data[lesson]["topic_name"]
        return name

    def topic_code(self, lesson):
        """Get topic number."""
        if (
            self.data[lesson]["topic_code"] != ""
            and self.data[lesson]["topic_code"] is not None
        ):
            code = f" ({self.data[lesson]['topic_code']}) "
        else:
            code = " "
        return code

    def short_disc_name(self, discipline_id):
        """Get discipline short name."""
        data = self.plan_disciplines
        for i in range(len(data)):
            if data[i]["id"] == str(discipline_id):
                return data[i]["name_short"]
