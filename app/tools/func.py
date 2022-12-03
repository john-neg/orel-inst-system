import httpx


async def rewriter(
        text,
        temperature=0.95,
        top_k=50,
        top_p=0.9,
        repetition_penalty=2.5,
        num_return_sequences=5,
):
    """
    https://sbercloud.ru/ru/datahub/rugpt3family/demo-rewrite

    :param text: оригинальный текст для переписывания
    :param temperature: параметр температуры текста для генерации. дефолтное значение 0.95
    :param top_k: параметр top_k текста для генерации. дефолтное значение 50
    :param top_p: параметр top_p текста для генерации. дефолтное значение 0.90
    :param repetition_penalty: штраф за повторные реплики. дефолтное значение 1.5
    :param num_return_sequences: кол-во примеров, из которых выбирается лучший рерайт. дефолтное значение 5
    :param range_mode: выбор режима ранжирования кандидатов ("bertscore", "classifier"). дефолтное значение bertscore
    :return: str
    """

    endpoint = "https://api.aicloud.sbercloud.ru/public/v2/rewriter/predict"

    data = {
      "instances": [
        {
          "text": text,
          "temperature": temperature,
          "top_k": top_k,
          "top_p": top_p,
          "repetition_penalty": repetition_penalty,
          "num_return_sequences": num_return_sequences,
          "range_mode": "all",
        }
      ]
    }

    headers = {
      'Content-Type': 'application/json'
    }

    r = httpx.post(endpoint, headers=headers, json=data, timeout=60)
    return r.json().get("prediction_best")
