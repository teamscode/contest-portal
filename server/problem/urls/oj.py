from django.conf.urls import url

from ..views.oj import ProblemTagAPI, ContestProblemAPI

urlpatterns = [
    url(r"^problem/tags/?$", ProblemTagAPI.as_view(), name="problem_tag_list_api"),
    url(r"^contest/problem/?$", ContestProblemAPI.as_view(), name="contest_problem_api"),
]
