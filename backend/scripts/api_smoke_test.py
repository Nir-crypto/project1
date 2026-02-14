import json
import os
import random
import string
import sys
import urllib.error
import urllib.request


BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000/api').rstrip('/')


class ApiError(Exception):
    pass


class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def request(self, method, path, token=None, payload=None):
        url = f"{self.base_url}{path}"
        body = None
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        if payload is not None:
            body = json.dumps(payload).encode('utf-8')

        req = urllib.request.Request(url, data=body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                text = resp.read().decode('utf-8')
                data = json.loads(text) if text else {}
                return resp.status, data
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode('utf-8')
            try:
                parsed = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                parsed = {'raw': raw}
            raise ApiError(f"{method} {path} failed with {exc.code}: {parsed}") from exc
        except urllib.error.URLError as exc:
            raise ApiError(f"Could not reach API server at {url}: {exc}") from exc


def random_email():
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"smoke_{suffix}@example.com"


def choose_option():
    return random.choice(['a', 'b', 'c', 'd'])


def main():
    random.seed(42)
    client = ApiClient(BASE_URL)

    print(f"[1/10] Fetching interests from {BASE_URL}/interests")
    _, interests = client.request('GET', '/interests')
    if not isinstance(interests, list) or len(interests) < 2:
        raise ApiError('Expected at least 2 interests for registration.')

    selected_interest_ids = [interests[0]['id'], interests[1]['id']]
    assessment_interest_id = interests[0]['id']

    email = random_email()
    register_payload = {
        'name': 'Smoke Tester',
        'email': email,
        'password': 'SmokePass123',
        'interests': selected_interest_ids,
    }
    print('[2/10] Registering test user')
    client.request('POST', '/auth/register', payload=register_payload)

    print('[3/10] Logging in')
    _, login_data = client.request('POST', '/auth/login', payload={'email': email, 'password': 'SmokePass123'})
    access_token = login_data.get('access')
    if not access_token:
        raise ApiError('Login did not return access token.')

    print('[4/10] Verifying profile and dashboard')
    client.request('GET', '/auth/me', token=access_token)
    client.request('GET', '/dashboard', token=access_token)

    print('[5/10] Starting adaptive assessment')
    _, start_data = client.request(
        'POST',
        '/assessment/start',
        token=access_token,
        payload={'interest_id': assessment_interest_id},
    )

    attempt_id = start_data.get('attempt_id')
    current_question = start_data.get('question')
    if not attempt_id or not current_question:
        raise ApiError('Assessment start did not return attempt/question payload.')

    print('[6/10] Answering adaptive questions until completion')
    adaptive_result = None
    for _ in range(30):
        payload = {
            'attempt_id': attempt_id,
            'question_id': current_question['id'],
            'selected_option': choose_option(),
            'time_spent': random.randint(8, 25),
        }
        _, answer_data = client.request('POST', '/assessment/answer', token=access_token, payload=payload)
        if answer_data.get('done'):
            adaptive_result = answer_data
            break
        current_question = answer_data.get('next_question')
        if not current_question:
            raise ApiError('Expected next_question for unfinished assessment response.')

    if not adaptive_result:
        raise ApiError('Adaptive assessment did not complete within loop guard.')

    print('[7/10] Fetching result payload by attempt id')
    _, result_data = client.request('GET', f'/result/{attempt_id}', token=access_token)
    recommended = result_data.get('recommended_courses', [])
    if not recommended:
        raise ApiError('Expected recommended courses in result response.')

    course_id = recommended[0]['id']

    print('[8/10] Starting final assessment')
    _, final_start = client.request('POST', '/final/start', token=access_token, payload={'course_id': course_id})
    final_questions = final_start.get('questions', [])
    if not final_questions:
        raise ApiError('Expected at least 1 final assessment question.')

    answers = [{'question_id': q['id'], 'selected_option': choose_option()} for q in final_questions]

    print('[9/10] Submitting final assessment')
    _, final_submit = client.request(
        'POST',
        '/final/submit',
        token=access_token,
        payload={'course_id': course_id, 'answers': answers},
    )

    passed = bool(final_submit.get('passed'))
    if passed:
        print('[10/10] Final passed -> submitting feedback')
        _, feedback_questions = client.request('GET', '/feedback/questions', token=access_token)
        response_payload = {
            str(item['id']): (item.get('options') or ['N/A'])[0]
            for item in feedback_questions
        }
        client.request(
            'POST',
            '/feedback/submit',
            token=access_token,
            payload={
                'course_id': course_id,
                'responses': response_payload,
                'comment': 'Smoke test feedback submission.',
            },
        )
        print('Smoke test completed: PASS (including feedback).')
    else:
        message = str(final_submit.get('message', ''))
        if 'Try again' not in message:
            raise ApiError('Expected fail message to include "Try again".')
        print('Smoke test completed: PASS (final assessment fail path validated).')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'SMOKE TEST FAILED: {exc}')
        sys.exit(1)
