from openpyxl.styles import Alignment, Border, Font, NamedStyle, PatternFill, Side


class ExcelStyle(object):
    """Стили оформления для экспортируемых файлов Excel."""

    ThinBorder = Side(style="thin", color="000000")
    ThickBorder = Side(style="thick", color="000000")
    AllBorder = Border(
        left=ThinBorder, right=ThinBorder, top=ThinBorder, bottom=ThinBorder
    )

    Header = NamedStyle(name="header")
    Header.font = Font(name="Times New Roman", size=12, bold=True)
    Header.border = AllBorder
    Header.alignment = Alignment(wrap_text=True)

    HeaderSmall = NamedStyle(name="header_small")
    HeaderSmall.font = Font(name="Times New Roman", size=10, bold=True)
    HeaderSmall.border = AllBorder
    HeaderSmall.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True,
                shrink_to_fit=True,
            )

    Base = NamedStyle(name="base")
    Base.font = Font(name="Times New Roman", size=11)
    Base.border = AllBorder
    Base.alignment = Alignment(wrap_text=True)

    Base_No_Wrap = NamedStyle(name="base_no_wrap")
    Base_No_Wrap.font = Font(name="Times New Roman", size=11)
    Base_No_Wrap.border = AllBorder
    # Base.alignment = Alignment(wrap_text=True)

    Number = NamedStyle(name="number")
    Number.font = Font(name="Times New Roman", size=9)
    Number.border = AllBorder
    Number.alignment = Alignment(
        horizontal="center", vertical="center", wrap_text=True, shrink_to_fit=True
    )

    BaseBold = NamedStyle(name="base_bold")
    BaseBold.font = Font(name="Times New Roman", size=11, bold=True)
    BaseBold.border = AllBorder
    BaseBold.alignment = Alignment(wrap_text=True)

    GreyFill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
