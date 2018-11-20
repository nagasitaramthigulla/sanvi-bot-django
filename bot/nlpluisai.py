import requests

headers = {
    'Ocp-Apim-Subscription-Key': 'a1dc8ec727b045b68c74e57ebdaac2b5',
}


def get_intent(message: str) -> dict:
    params = {
        # Query parameter
        'q': message
    }

    try:
        r = requests.get(
            'https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/eff4b45f-86c4-424d-afa0-8f4f3cb163c8',
            headers=headers, params=params)
        return r.json()
    except Exception as e:
        print(e)
    return {}
