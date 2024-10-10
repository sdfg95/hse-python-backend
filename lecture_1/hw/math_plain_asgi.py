import json
from statistics import mean
from math import factorial


async def app(scope, receive, send) -> None:
    assert scope['type'] == 'http'

    if scope['method'] == 'GET':
        await handle_get_request(scope, receive, send)
    else:
        await send_error(send, 404, 'Not found')


async def handle_get_request(scope, receive, send):
    path = scope['path']
    if path == '/factorial':
        await process_factorial(scope, send)
    elif path.startswith('/fibonacci'):
        await process_fibonacci(scope, send)
    elif path == '/mean':
        await process_mean(scope, receive, send)
    else:
        await send_error(send, 404, 'Not found')


async def process_factorial(scope, send):
    n_val = extract_query_param(scope.get('query_string', b''), 'n')
    if n_val is None:
        await send_error(send, 422, "Unprocessable Entity")
        return

    valid, n = validate_n(n_val)
    if not valid:
        await send_error(send, 400 if n == -2 else 422, "Bad request" if n == -2 else "Unprocessable Entity")
        return

    result = factorial(n)
    await send_response(send, 200, {"result": result})


async def process_fibonacci(scope, send):
    n_val = extract_path_param(scope['path'])
    if n_val is None:
        await send_error(send, 422, "Unprocessable Entity")
        return

    valid, n = validate_n(n_val)
    if not valid:
        await send_error(send, 400 if n == -2 else 422, "Bad request" if n == -2 else "Unprocessable Entity")
        return

    result = fibonacci(n)
    await send_response(send, 200, {"result": result})


async def process_mean(scope, receive, send):
    numbers = await get_request_body(receive)
    if numbers is None:
        await send_error(send, 422, 'Unprocessable Entity')
        return

    if not isinstance(numbers, list) or not all(isinstance(num, (int, float)) for num in numbers):
        await send_error(send, 422, 'Unprocessable Entity')
        return

    if not numbers:
        await send_error(send, 400, 'Bad request')
        return

    result = mean(numbers)
    await send_response(send, 200, {"result": result})


async def send_error(send, status_code, message):
    await send_response(send, status_code, {"error": message})


async def send_response(send, status_code, response_data):
    response_body = json.dumps(response_data).encode('utf-8')
    await send({
        'type': 'http.response.start',
        'status': status_code,
        'headers': [(b'content-type', b'application/json')],
    })
    await send({
        'type': 'http.response.body',
        'body': response_body,
    })


def extract_query_param(query_string, param):
    params = parse_query_string(query_string.decode('utf-8'))
    return params.get(param)


def parse_query_string(query_string):
    return dict(param.split('=') for param in query_string.split('&')) if query_string else {}


def extract_path_param(path_string):
    return path_string.split('/')[-1]


def validate_n(n):
    if n is None:
        return False, -1
    try:
        n = int(n)
    except ValueError:
        return False, -1

    if n < 0:
        return False, -2
    return True, n


async def get_request_body(receive):
    body = b""
    while True:
        message = await receive()
        if message['type'] == 'http.request':
            body += message.get('body', b'')
            if not message.get('more_body'):
                break
    return json.loads(body) if body else None


def fibonacci(n):
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b