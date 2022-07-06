from __future__ import annotations

from phpserialize import loads

from app.common.func.api_get import api_get_db_table, check_api_db_response
from app.common.func.app_core import data_processor
from config import ApeksConfig as Apeks


async def get_system_reports_data(
    report_id: int | str,
    table_name: str = Apeks.TABLES.get("system_reports"),
) -> dict:
    """Получение данных о настройках системных отчетов Апекс-ВУЗ"""
    table_data = data_processor(
        await check_api_db_response(
            await api_get_db_table(table_name, id=report_id)
        )
    )
    settings = table_data[report_id].get('settings')
    reports_data = dict(
        loads(settings.encode(), decode_strings=True)
    )
    return reports_data
