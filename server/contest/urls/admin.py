from django.conf.urls import url

from ..views.admin import ContestAnnouncementAPI, ContestAPI, DownloadContestSubmissions, TeamReviewActionAPI

urlpatterns = [
    url(r"^contest/?$", ContestAPI.as_view(), name="contest_admin_api"),
    url(r"^contest/announcement/?$", ContestAnnouncementAPI.as_view(), name="contest_announcement_admin_api"),
    url(r"^download_submissions/?$", DownloadContestSubmissions.as_view(), name="download_submission"),
    url(r"^team_review/?$", TeamReviewActionAPI.as_view(), name="team_review_action_api"),
]
