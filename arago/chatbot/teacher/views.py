from typing import Any
import json
import re
from contextlib import suppress

from django.http import HttpRequest, JsonResponse
from django.http.response import HttpResponse as HttpResponse

from .models import Teacher
from chatbot.kakao import ChatbotView


# Create your views here.
class TeacherView(ChatbotView):
    action = None

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self.action == "all":
            resp = self.post_all()
        elif self.action == "name":
            resp = self.post_name(request)
        return resp

    def convert_query_sets_text(self, query_sets) -> str:
        texts = []
        for row in query_sets:
            line = " ".join([f"{row[key]} " for key in row])  # 쿼리셋을 문자열로 변환
            texts.append(line)

        texts = "\n".join(texts)  # 하나의 문자열로 통합
        return texts

    # def create_list_output(self, teachers):
    #     query_sets = teachers.values("name", "subject", "role")  # DB에서 가져올 데이터
    #     texts = self.convert_query_sets_text(query_sets)
    #     output = {"simpleText": {"text": texts}}  # 카카오톡 메시지 형식에 맞춤
    #     return output

    def post_name(self, request):
        try:
            payload = json.loads(request.body)
            patt = r"[가-힣a-zA-Z]+"
            name_parameter = payload["action"]["params"]["teacher_name"]
            match_result = re.match(patt, name_parameter)

            assert match_result, "이름 형식이 아닌것 같아요. 이름을 입력해 주세요."

            teacher_name = match_result.group()
            query_sets = Teacher.objects.filter(
                name=teacher_name
            )  # 동명이인이 있을 수도 있으니까 배열로 반환

            if not len(query_sets):
                raise Teacher.DoesNotExist("아라고등학교 선생님이 아닌것 같아요.")

            # output = self.create_list_output(query_sets)

        except Exception as e:
            output = {"simpleText": {"text": str(e)}}

        finally:
            message = self.create_response_message(output)
            return JsonResponse(message)

    def post_all(self):
        teachers = Teacher.objects.values_list("name", "subject", "role")
        query_sets = teachers.values("name", "subject", "role")  # DB에서 가져올 데이터
        texts = self.convert_query_sets_text(query_sets)
        output = {"simpleText": {"text": texts}}  # 카카오톡 메시지 형식에 맞춤
        # output = self.create_list_output(teachers)
        message = self.create_response_message(output)
        return JsonResponse(message)  # 메시지 전송
