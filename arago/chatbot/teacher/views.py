from copy import deepcopy
from typing import Any
import json
import re

from django.http import HttpRequest, JsonResponse
from django.http.response import HttpResponse as HttpResponse

from .models import Teacher
from chatbot.kakao import ChatbotView

MAP_BLOCK_ID = "66667a153d1a600a8a3acc34"
# Create your views here.
class MapView(ChatbotView):
    def post(self, request):
        body = request.body.decode("utf-8")
        payload = json.loads(body)
        action = payload["action"]
        parameters = action["params"]
        extra_parameters = action["clientExtra"]
        office_name = parameters.get("office_name") if parameters.get("office_name") else extra_parameters.get("office_name")
        
        try:
            office_image_maps = {"예능환경":"https://wimg.mk.co.kr/news/cms/202312/15/news-p.v1.20231204.469decf4893d47f68cce5fc3bfbe0309_P1.jpg",
                                    "창의환경":"https://i.namu.wiki/i/zN7ASE4kyQNHO9jeAobgriDh2fqdbqiJVk5v7K-Tb_bCtOtem2v47wkFV4cQfYJYwbjr7bgoVqKVyHkp_Gy_6A.webp",
                                    "융합정보":"https://blog.kakaocdn.net/dn/15c1u/btrBF5rq2s1/uCDT0O1GSpm5WEu8kHzna0/img.jpg"} #교무실 별 약도
        
            if office_name:
                outputs = {"simpleImage":{"imageUrl": "","altText":"교무실 약도 입니다"}}
                image_url = office_image_maps.get(office_name)
                assert image_url,"교무실 이름이 정확하지 않아요" #교무실 이름이 잘못됐습니다.
                outputs["simpleImage"]["imageUrl"] = image_url
                
            else:
                office_names = office_image_maps.keys()
                text_card_template = {
                    "textCard":{
                    "title":"교무실을 지정해주세요",
                    "description":"위치를 확인할 교무실을 지정해주세요",
                    "buttons":[]
                    }
                }
                button_template = {
                                "action": "block",
                                "blockId": MAP_BLOCK_ID,
                                "label": "",
                                "extra": {"office_name": ""},
                            }
                buttons = text_card_template["textCard"]["buttons"] 
                
                for office_name in office_names:
                    new_button = deepcopy(button_template)
                    new_button["label"] = office_name
                    new_button["extra"]["office_name"] = office_name
                    buttons.append(new_button)
                
                outputs = text_card_template

        
        except Exception as e:
            outputs = {"simpleText": {"text": str(e)}}

        finally:
            message = self.create_response_message(outputs)    
            return JsonResponse(message)
    

class TeacherView(ChatbotView):
    action = None
    button_template = {
        "action": "block",
        "blockId": MAP_BLOCK_ID,
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
