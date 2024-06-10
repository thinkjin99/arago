from django.db import models


# Create your models here.
class Teacher(models.Model):
    name = models.CharField(max_length=30, verbose_name="이름")
    subject = models.CharField(
        max_length=20, verbose_name="과목", blank=True, null=True
    )  # 담당 과목
    office_name = models.CharField(max_length=30, blank=True, null=True)
    floor = models.IntegerField(default=1)

    class Meta:
        db_table = "teacher"
