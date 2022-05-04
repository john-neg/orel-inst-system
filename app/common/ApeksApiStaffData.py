from app.main.func import get_active_staff_id, get_data, db_request, db_filter_req
from config import ApeksConfig as Apeks


class ApeksApiStaffData:
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
