from django.db import models


# Create your models here.
class Teacher(models.Model):
    name = models.CharField(max_length=30, verbose_name="이름")
    subject = models.CharField(
        max_length=20, verbose_name="과목", blank=True, null=True
    )  # 담당 과목
    role = models.CharField(
        max_length=10, verbose_name="역할", blank=True, null=True
    )  # 상담 선생님, 진로 선생님, 체육 부장 등의 역할
    map_image = models.ImageField(blank=False, verbose_name="약도")

    class Meta:
        db_table = "teacher"
