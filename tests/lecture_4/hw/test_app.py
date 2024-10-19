import base64
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from http import HTTPStatus

from pydantic import SecretStr

from lecture_4.demo_service.api.main import create_app
from lecture_4.demo_service.core.users import (
    UserEntity,
    UserInfo,
    UserRole,
    UserService,
    password_is_longer_than_8,
)

from lecture_4.demo_service.api.contracts import (
    UserAuthRequest,
    UserResponse,
    RegisterUserRequest,
)

TEST_DATA_DICT = {
    "username": "nagibator340",
    "name": "chuck noris",
    "birthdate": "1999-01-01T00:20:00",
    "password": "megatron2000",
    "uid": 2,
    "role": UserRole.USER
}


def encode_credentials(username, password):
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return encoded_credentials


@pytest.fixture
def user_info():
    return UserInfo(
        username=TEST_DATA_DICT["username"],
        name=TEST_DATA_DICT["name"],
        birthdate=TEST_DATA_DICT["birthdate"],
        role=UserRole.USER,
        password=SecretStr(TEST_DATA_DICT["birthdate"])
    )


@pytest.fixture
def user_entity(info: UserInfo):
    return UserEntity(
        uid=1,
        inf0=info
    )


@pytest.fixture
def register_user_request():
    return RegisterUserRequest(
        username=TEST_DATA_DICT["username"],
        name=TEST_DATA_DICT["name"],
        birthdate=TEST_DATA_DICT["birthdate"],
        password=TEST_DATA_DICT["password"]
    )


@pytest.fixture()
def register_user_request_json(register_user_request: RegisterUserRequest):
    request_data = register_user_request.model_dump()
    request_data["birthdate"] = register_user_request.birthdate.isoformat()
    request_data["password"] = register_user_request.password.get_secret_value()
    return request_data


@pytest.fixture
def user_response():
    return UserResponse(
        uid=1,
        username=TEST_DATA_DICT["username"],
        name=TEST_DATA_DICT["name"],
        birthdate=TEST_DATA_DICT["birthdate"],
        role=UserRole.USER
    )


@pytest.fixture()
def user_authorisation_request():
    return UserAuthRequest(
        username=TEST_DATA_DICT["username"],
        password=SecretStr(TEST_DATA_DICT["password"])
    )


@pytest.fixture
def user_service():
    return UserService


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


@pytest.fixture()
def app_instance():
    application = create_app()
    with TestClient(application) as client_instance:
        yield client_instance


@pytest.fixture()
def auth_headers():
    return {
        "Authorization": f"Basic {encode_credentials(TEST_DATA_DICT['username'], TEST_DATA_DICT['password'])}"
    }


@pytest.fixture()
def admin_headers():
    return {
        "Authorization": f"Basic {encode_credentials('admin', 'superSecretAdminPassword123')}"
    }


def test_register_user(app_instance: TestClient, register_user_request_json: dict):
    response = app_instance.post(
        "/user-register", json=register_user_request_json
    )
    data = response.json()
    assert response.status_code == HTTPStatus.OK
    for key, _ in data.items():
        assert data[key] == TEST_DATA_DICT[key]


def test_second_registration(app_instance: TestClient, register_user_request_json: dict):
    _ = app_instance.post(
        "/user-register", json=register_user_request_json
    )
    response = app_instance.post(
        "/user-register", json=register_user_request_json
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_user_by_id(app_instance: TestClient, register_user_request_json: dict, auth_headers: dict,
                        user_response: UserResponse):
    register_resp = app_instance.post(
        "/user-register", json=register_user_request_json
    )

    assert register_resp.status_code == HTTPStatus.OK

    response = app_instance.post(
        url='/user-get',
        params={'id': register_resp.json().get('uid')},
        headers=auth_headers

    )

    assert response.status_code == HTTPStatus.OK
    assert response.json().get("name") == user_response.name
    assert response.json().get("username") == user_response.username
    assert response.json().get("role") == user_response.role
    assert datetime.fromisoformat(response.json().get("birthdate")) == user_response.birthdate


def test_get_user_by_username(app_instance: TestClient, register_user_request_json: dict, auth_headers: dict,
                              user_response: UserResponse):
    register_resp = app_instance.post(
        "/user-register", json=register_user_request_json
    )

    assert register_resp.status_code == HTTPStatus.OK

    response = app_instance.post(
        url='/user-get',
        params={'username': register_resp.json().get('username')},
        headers=auth_headers

    )

    assert response.status_code == HTTPStatus.OK
    assert response.json().get("name") == user_response.name
    assert response.json().get("username") == user_response.username
    assert response.json().get("role") == user_response.role
    assert datetime.fromisoformat(response.json().get("birthdate")) == user_response.birthdate


def test_get_user_by_both_params(app_instance: TestClient, register_user_request_json: dict, auth_headers: dict):
    register_resp = app_instance.post(
        "/user-register", json=register_user_request_json
    )

    assert register_resp.status_code == HTTPStatus.OK

    response = app_instance.post(
        url='/user-get',
        params={'username': register_resp.json().get('username'),
                'id': register_resp.json().get('uid')},
        headers=auth_headers

    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_user_by_both_params_one_incorrect(app_instance: TestClient, register_user_request_json: dict,
                                               auth_headers: dict):
    register_resp = app_instance.post(
        "/user-register", json=register_user_request_json
    )

    assert register_resp.status_code == HTTPStatus.OK

    response = app_instance.post(
        url='/user-get',
        params={'username': register_resp.json().get('username'),
                'id': 5},
        headers=auth_headers

    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_user_no_register(app_instance: TestClient, register_user_request_json: dict, auth_headers: dict):
    response = app_instance.post(
        url='/user-get',
        params={'username': register_user_request_json.get('username')},
        headers=auth_headers

    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_user_incorrect_params(app_instance: TestClient, register_user_request_json: dict, auth_headers: dict):
    register_resp = app_instance.post(
        "/user-register", json=register_user_request_json
    )

    assert register_resp.status_code == HTTPStatus.OK

    response = app_instance.post(
        url='/user-get',
        params={'username': "Jason Statem"},
        headers=auth_headers

    )
    assert response.status_code == HTTPStatus.NOT_FOUND

    response = app_instance.post(
        url='/user-get',
        params={'id': 4},
        headers=auth_headers

    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_user_no_params(app_instance: TestClient, register_user_request_json: dict, auth_headers: dict):
    register_resp = app_instance.post(
        "/user-register", json=register_user_request_json
    )

    assert register_resp.status_code == HTTPStatus.OK

    response = app_instance.post(
        url='/user-get',
        headers=auth_headers

    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_user_no_header(app_instance: TestClient, register_user_request_json: dict, auth_headers: dict):
    register_resp = app_instance.post(
        "/user-register", json=register_user_request_json
    )

    assert register_resp.status_code == HTTPStatus.OK

    response = app_instance.post(
        url='/user-get',
        params={'username': "Jason Statem"}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_user_wrong_header(app_instance: TestClient, register_user_request_json: dict, auth_headers: dict):
    register_resp = app_instance.post(
        "/user-register", json=register_user_request_json
    )
    assert register_resp.status_code == HTTPStatus.OK

    response = app_instance.post(
        url='/user-get',
        params={'username': "Jason Statem"},
        headers={
            "Authorization": f"Basic {encode_credentials('rokki', 'bolboa')}"
        }
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_promote_user(app_instance: TestClient, register_user_request_json: dict, auth_headers: dict):
    register_resp = app_instance.post(
        "/user-register", json=register_user_request_json
    )
    assert register_resp.status_code == HTTPStatus.OK

    response = app_instance.post(
        url='/user-promote',
        params={'id': register_user_request_json.get('uid')},
        headers=auth_headers
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_promote_user_admin(app_instance: TestClient, register_user_request_json: dict, admin_headers: dict):
    register_resp = app_instance.post(
        "/user-register", json=register_user_request_json
    )
    assert register_resp.status_code == HTTPStatus.OK

    response = app_instance.post(
        url='/user-promote',
        params={'id': 1},
        headers=admin_headers
    )

    assert response.status_code == HTTPStatus.OK