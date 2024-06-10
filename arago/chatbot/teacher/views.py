from copy import deepcopy
from typing import Any
import json
import re

from django.http import HttpRequest, JsonResponse
from django.http.response import HttpResponse as HttpResponse

from .models import Teacher
from chatbot.kakao import ChatbotView

    
# Create your views here.
class MapView(ChatbotView):
    def post(self, request):
        body = request.body.decode("utf-8")
        payload = json.loads(body)
        parameters = payload["action"]["params"]
        offic_name = parameters.get("office_name")
        try:
            assert offic_name, "교무실 이름을 입력해 주세요."
            outputs = {"simpleImage":{"imageUrl": "","altText":"교무실 약도 입니다"}}
            
            if offic_name == "test1":
                image_url = "https://wimg.mk.co.kr/news/cms/202312/15/news-p.v1.20231204.469decf4893d47f68cce5fc3bfbe0309_P1.jpg"
            elif offic_name == "test2":
                image_url = "https://i.namu.wiki/i/zN7ASE4kyQNHO9jeAobgriDh2fqdbqiJVk5v7K-Tb_bCtOtem2v47wkFV4cQfYJYwbjr7bgoVqKVyHkp_Gy_6A.webp"
            elif offic_name == "test3":
                image_url = "https://blog.kakaocdn.net/dn/15c1u/btrBF5rq2s1/uCDT0O1GSpm5WEu8kHzna0/img.jpg"
            else:
                raise AssertionError("교무실 이름이 정확하지 않아요")
            
            #이미지 링크만 다르게 변조해서 반환        
            outputs["simpleImage"]["imageUrl"] = image_url
            message = self.create_response_message(outputs)    
        
        except Exception as e:
            outputs = {"simpleText": {"text": str(e)}}

        finally:
            return JsonResponse(message)
    

class TeacherView(ChatbotView):
    action = None
    button_template = {
        "action": "block",
        "blockId": "fsafsafasr21512",
        "label": "약도보기",
        "extra": {"office_name": ""},
    }

    card_template = {
        "title": "",
        "description": "선생님 정보",
        "itemList": [],
        "buttons": [],
    }

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self.action == "all":
            resp = self.post_all()
        elif self.action == "name":
            resp = self.post_name(request)
        return resp

    def post_name(self, request):
        try:
            body = request.body.decode("utf-8")
            payload = json.loads(body)
            patt = r"[가-힣a-zA-Z]+"
            parameters = payload["action"]["params"]

            name_parameter = parameters.get("teacher_name")
            assert name_parameter, "선생님 이름을 입력해 주세요."

            match_result = re.match(patt, name_parameter)
            assert match_result, "이름 형식이 아닌것 같아요. 이름을 입력해 주세요."

            teacher_name = match_result.group()
            query_sets = Teacher.objects.filter(name=teacher_name).values(
                "name", "subject", "office_name", "floor"
            )  # 동명이인이 있을 수도 있으니까 배열로 반환

            if not len(query_sets):
                raise Teacher.DoesNotExist("아라고등학교 선생님이 아닌것 같아요.")

            outputs = []

            for row in query_sets:
                new_button = deepcopy(self.button_template) #템플릿 복사
                new_card = deepcopy(self.card_template)

                new_button["extra"] = {"office_name": row["office_name"]}
                new_card["buttons"].append(new_button)

                new_card["title"] = row["name"] + " 선생님"
                items = [{"title": key, "description": row[key]} for key in row]
                new_card["itemList"] = items

                outputs.append({"itemCard":new_card})

        except Exception as e:
            outputs = {"simpleText": {"text": str(e)}}

        finally:
            message = self.create_response_message(outputs)
            return JsonResponse(message)

    def post_all(self):
        query_sets = Teacher.objects.values(
            "name", "subject", "office_name", "floor"
        )  # DB에서 가져올 데이터
        teaher_infos = [
            f"{row["name"]} // {row["subject"]} // {row["floor"]}층 {row["office_name"]}"
            for row in query_sets
        ]

        texts = "\n".join(teaher_infos)
        output = {"simpleText": {"text": texts}}  # 카카오톡 메시지 형식에 맞춤
        message = self.create_response_message(output)
        return JsonResponse(message)  # 메시지 전송
