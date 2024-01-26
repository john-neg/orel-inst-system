from dataclasses import dataclass


@dataclass
class Staff:
    staff_id: int
    name: str
    position: str
    sort: int


@dataclass
class StaffAbsence:
    name: int
    ## Может dict[int, str] и убрать Staff
    staff: list[Staff]


@dataclass
class StableStaffDeptData:
    dept_id: int
    name: str
    dept_type: str
    total: int
    absence: list[StaffAbsence]
    user: str
    updated: str


@dataclass
class StableStaff:
    date: str
    departments: list[StableStaffDeptData]
    status: str
