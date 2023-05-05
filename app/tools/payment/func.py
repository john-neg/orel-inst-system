# import logging
# from http import HTTPStatus
# from json import JSONDecodeError
#
# import httpx
# from httpx import ReadTimeout
#
# REWRITER_ENDPOINT = "https://api.aicloud.sbercloud.ru/public/v2/rewriter/predict"
#
#
# async def rewriter(
#     text: str,
#     endpoint: str = REWRITER_ENDPOINT,
#     temperature: float = 0.95,
#     top_k: int = 50,
#     top_p: float = 0.95,
#     repetition_penalty: float = 2.5,
#     num_return_sequences: int = 5,
#     get_code: bool = False,
# ):
#     """
#     https://sbercloud.ru/ru/datahub/rugpt3family/demo-rewrite
#
#     :param text: оригинальный текст для переписывания
#     :param endpoint: API endpoint
#     :param temperature: параметр температуры текста для генерации. дефолтное значение 0.95
#     :param top_k: параметр top_k текста для генерации. дефолтное значение 50
#     :param top_p: параметр top_p текста для генерации. дефолтное значение 0.90
#     :param repetition_penalty: штраф за повторные реплики. дефолтное значение 1.5
#     :param num_return_sequences: кол-во примеров, из которых выбирается лучший рерайт. дефолтное значение 5
#     :param get_code: возвращает статус ответа API если True. По умолчанию False.
#     :return: str
#     """
#
#     data = {
#         "instances": [
#             {
#                 "text": text,
#                 "temperature": temperature,
#                 "top_k": top_k,
#                 "top_p": top_p,
#                 "repetition_penalty": repetition_penalty,
#                 "num_return_sequences": num_return_sequences,
#                 "range_mode": "all",
#             }
#         ]
#     }
#
#     headers = {"Content-Type": "application/json"}
#
#     if get_code:
#         try:
#             status = httpx.post(
#                 endpoint, headers=headers, json=data, timeout=10
#             ).status_code
#         except ReadTimeout:
#             status = HTTPStatus.GATEWAY_TIMEOUT
#         return status
#
#     r = httpx.post(endpoint, headers=headers, json=data, timeout=120)
#     try:
#         resp_json = r.json()
#         logging.debug(
#             f"Выполнен запрос к API Rewriter - 'temperature': {temperature}, "
#             f"'top_k': {top_k}, 'top_p': {top_p}, "
#             f"'repetition_penalty': {repetition_penalty}, "
#             f"'num_return_sequences': {num_return_sequences}"
#         )
#         return resp_json
#     except JSONDecodeError as error:
#         logging.error(
#             f"Ошибка конвертации ответа API Rewriter в JSON: '{error}'"
#         )
#
#
# async def combine_dict(*args: dict) -> dict:
#     """
#     Объединяет словари в 1.
#
#     :return: dict {key: [values]}
#     """
#     result_dict = {}
#     for dct in args:
#         for key in dct:
#             if isinstance(dct[key], list):
#                 result_dict.setdefault(key, []).extend(dct[key])
#             else:
#                 result_dict.setdefault(key, []).append(dct[key])
#     return result_dict
