import json
import logging

import pytest
from django.test import Client
from django.urls import reverse

logger = logging.getLogger("test")

kakao_test_message = {
    "bot": {"id": "<봇 id>", "name": "<봇 이름>"},
    "intent": {
        "id": "<블록 id>",
        "name": "지식+",
        "extra": {
            "reason": {"code": 1, "message": "OK"},
            "knowledge": {
                "responseType": "skill",
                "matchedKnowledges": [
                    {
                        "categories": [
                            "<카테고리 1>",
                            "<카테고리 2>",
                            "<카테고리 3>",
                            "<카테고리 4>",
                        ],
                        "question": "<질문>",
                        "answer": "<답변>",
                        "imageUrl": "<이미지 url>",
                        "landingUrl": "<랜딩 url>",
                    },
                    {
                        "categories": [
                            "<카테고리 1>",
                            "<카테고리 2>",
                            "<카테고리 3>",
                            "<카테고리 4>",
                        ],
                        "question": "<질문>",
                        "answer": "<답변>",
                        "imageUrl": "<이미지 url>",
                        "landingUrl": "<랜딩 url>",
                    },
                ],
            },
        },
    },
    "action": {
        "id": "<액션 id>",
        "name": "<액션 이름>",
        "params": {"teacher_name": "정명진", "office_name": "test1"},
        "detailParams": {},
        "clientExtra": {},
    },
    "userRequest": {
        "block": {"id": "<블록 id>", "name": "<블록 이름>"},
        "user": {
            "id": "<사용자 botUserKey>",
            "type": "botUserKey",
            "properties": {"botUserKey": "<사용자 botUserKey>"},
        },
        "utterance": "<사용자 발화>",
        "params": {
            "surface": "BuilderBotTest",
            "ignoreMe": "true",
            "teacher_name": "정명진",
        },
        "lang": "ko",
        "timezone": "Asia/Seoul",
    },
    "contexts": [],
}


@pytest.mark.django_db
class TestTeacher:

    def test_teacher_all(self):
        client = Client()
        url = reverse("teacher:all")
        response = client.post(path=url, data=kakao_test_message)
        logging.debug(response.content)
        assert response.status_code == 200

    def test_teacher_name(self):
        client = Client()
        url = reverse("teacher:info")
        response = client.post(
            path=url,
            data=json.dumps(kakao_test_message),
            content_type="application/json",
        )
        logging.debug(response.content)
        assert response.status_code == 200

    def test_teacher_map(self):
        client = Client()
        url = reverse("teacher:map")
        response = client.post(
            path=url,
            data=json.dumps(kakao_test_message),
            content_type="application/json",
        )
        logging.debug(response.content)
        assert response.status_code == 200
