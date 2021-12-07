from app.main.func import db_request, db_filter_req, get_active_staff_id, get_data
from app.schedule.func import get_lessons, get_disc_list


class ApeksStaffData:
    def __init__(self):
        self.active_staff_id = get_active_staff_id()
        self.data = get_data(self.active_staff_id)
        self.staff = self.data["staff"]
        self.departments = self.data["departments"]

    def get_staff(self, department_id):
        """getting staff ID and sorting them by position at the department"""

        def staff_sort(staff_id):
            """getting sorting code by position"""
            position_id = ""
            for history in state_staff_history:
                if history.get("staff_id") == str(staff_id):
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
            sort_dict[i] = int(staff_sort(i))
        a = sorted(sort_dict.items(), key=lambda x: x[1], reverse=True)
        prepod_dict = {}
        for i in range(len(a)):
            prepod_dict[a[i][0]] = self.staff_name(a[i][0], department_id)
        return prepod_dict

    def staff_name(self, staff_id, department_id):
        """short staff name without rank"""
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

    def calendarname(self, lesson):
        """combined topic + discipline name for calendar"""
        class_type_name = self.data[lesson]["class_type_name"]
        text = (
            class_type_name
            + self.topic_code(lesson)
            + self.shortdiscname(self.data[lesson]["discipline_id"])
            + " "
            + self.data[lesson]["groupName"]
        )
        return text

    def timestart_xlsx(self, lesson):
        """time start lesson for xlsx"""
        time = self.data[lesson]["lessonTime"].split(" - ")
        fulltime = self.data[lesson]["date"] + " " + time[0]
        return fulltime

    def timestart_ical(self, lesson):
        """time start lesson for iCal"""
        date = self.data[lesson]["date"].split(".")
        time = self.data[lesson]["lessonTime"].split(" - ")[0]
        utffix = str(int(time.split(":")[0]) - 3)
        if len(utffix) < 2:
            utffix = f"0{utffix}"
        return date[2] + date[1] + date[0] + "T" + utffix + time.split(":")[1] + "00Z"

    def timeend_ical(self, lesson):
        """time end lesson for iCal"""
        date = self.data[lesson]["date"].split(".")
        time = self.data[lesson]["lessonTime"].split(" - ")[1]
        utffix = str(int(time.split(":")[0]) - 3)
        if len(utffix) < 2:
            utffix = f"0{utffix}"
        return date[2] + date[1] + date[0] + "T" + utffix + time.split(":")[1] + "00Z"

    def topic_name(self, lesson):
        """get topic name"""
        if self.data[lesson]["topic_name"] is None:
            name = " "
        else:
            name = self.data[lesson]["topic_name"]
        return name

    def topic_code(self, lesson):
        """get topic number"""
        if (
            self.data[lesson]["topic_code"] != ""
            and self.data[lesson]["topic_code"] is not None
        ):
            code = " (" + self.data[lesson]["topic_code"] + ") "
        else:
            code = " "
        return code

    def shortdiscname(self, discipline_id):
        """get discipline short name"""
        data = self.plan_disciplines
        for i in range(len(data)):
            if data[i]["id"] == str(discipline_id):
                return data[i]["name_short"]
