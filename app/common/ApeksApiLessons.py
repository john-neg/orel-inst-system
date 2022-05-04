


class ApeksLessons:
    def __init__(self, staff_id, month, year):
        self.data = get_lessons(staff_id, month, year)
        self.plan_disciplines = get_disc_list()

    def calendar_name(self, lesson):
        """Combined topic + discipline name for calendar."""
        class_type_name = self.data[lesson]["class_type_name"]
        text = (
                f'{class_type_name}{self.topic_code(lesson)}'
                f'{self.short_disc_name(self.data[lesson]["discipline_id"])} '
                f'{self.data[lesson]["groupName"]}'
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
