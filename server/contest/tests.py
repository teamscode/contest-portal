import copy
from datetime import datetime, timedelta
from unittest import mock

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from account.models import AdminType
from utils.api.tests import APITestCase
from utils.constants import CacheKey

from .models import ContestAnnouncement, Contest, ContestRank

DEFAULT_CONTEST_DATA = {"title": "test title", "description": "test description",
                        "start_time": timezone.localtime(timezone.now()),
                        "end_time": timezone.localtime(timezone.now()) + timedelta(days=1),
                        "password": "123",
                        "allowed_ip_ranges": [],
                        "division": "Intermediate",
                        "visible": True, "real_time_rank": True}


class ContestAdminAPITest(APITestCase):
    def setUp(self):
        self.create_super_admin()
        self.url = self.reverse("contest_admin_api")
        self.data = copy.deepcopy(DEFAULT_CONTEST_DATA)

    def test_create_contest(self):
        response = self.client.post(self.url, data=self.data)
        self.assertSuccess(response)
        return response

    def test_create_contest_with_invalid_cidr(self):
        self.data["allowed_ip_ranges"] = ["127.0.0"]
        resp = self.client.post(self.url, data=self.data)
        self.assertTrue(resp.data["data"].endswith("is not a valid cidr network"))

    def test_update_contest(self):
        id = self.test_create_contest().data["data"]["id"]
        update_data = {"id": id, "title": "update title",
                       "description": "update description",
                       "password": "12345",
                       "division": "Intermediate",
                       "visible": False, "real_time_rank": False}
        data = copy.deepcopy(self.data)
        data.update(update_data)
        response = self.client.put(self.url, data=data)
        self.assertSuccess(response)
        response_data = response.data["data"]
        for k in data.keys():
            if isinstance(data[k], datetime):
                continue
            self.assertEqual(response_data[k], data[k])

    def test_get_contests(self):
        self.test_create_contest()
        response = self.client.get(self.url)
        self.assertSuccess(response)

    def test_get_one_contest(self):
        id = self.test_create_contest().data["data"]["id"]
        response = self.client.get("{}?id={}".format(self.url, id))
        self.assertSuccess(response)


class ContestAPITest(APITestCase):
    def setUp(self):
        user = self.create_admin()
        self.contest = Contest.objects.create(created_by=user, **DEFAULT_CONTEST_DATA)
        self.url = self.reverse("contest_api") + "?id=" + str(self.contest.id)

    def test_get_contest_list(self):
        url = self.reverse("contest_list_api")
        response = self.client.get(url + "?limit=10")
        self.assertSuccess(response)
        self.assertEqual(len(response.data["data"]["results"]), 1)

    def test_get_one_contest(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)

    def test_regular_user_validate_contest_password(self):
        self.create_user("test", "test123")
        url = self.reverse("contest_password_api")
        resp = self.client.post(url, {"contest_id": self.contest.id, "password": "error_password"})
        self.assertDictEqual(resp.data, {"error": "error", "data": "Wrong password or password expired"})

        resp = self.client.post(url, {"contest_id": self.contest.id, "password": DEFAULT_CONTEST_DATA["password"]})
        self.assertSuccess(resp)

    def test_regular_user_access_contest(self):
        self.create_user("test", "test123")
        url = self.reverse("contest_access_api")
        resp = self.client.get(url + "?contest_id=" + str(self.contest.id))
        self.assertFalse(resp.data["data"]["access"])

        password_url = self.reverse("contest_password_api")
        resp = self.client.post(password_url,
                                {"contest_id": self.contest.id, "password": DEFAULT_CONTEST_DATA["password"]})
        self.assertSuccess(resp)
        resp = self.client.get(self.url)
        self.assertSuccess(resp)


class ContestAnnouncementAdminAPITest(APITestCase):
    def setUp(self):
        self.create_super_admin()
        self.url = self.reverse("contest_announcement_admin_api")
        contest_id = self.create_contest().data["data"]["id"]
        self.data = {"title": "test title", "content": "test content", "contest_id": contest_id, "visible": True}

    def create_contest(self):
        url = self.reverse("contest_admin_api")
        data = DEFAULT_CONTEST_DATA
        return self.client.post(url, data=data)

    def test_create_contest_announcement(self):
        response = self.client.post(self.url, data=self.data)
        self.assertSuccess(response)
        return response

    def test_delete_contest_announcement(self):
        id = self.test_create_contest_announcement().data["data"]["id"]
        response = self.client.delete("{}?id={}".format(self.url, id))
        self.assertSuccess(response)
        self.assertFalse(ContestAnnouncement.objects.filter(id=id).exists())

    def test_get_contest_announcements(self):
        self.test_create_contest_announcement()
        response = self.client.get(self.url + "?contest_id=" + str(self.data["contest_id"]))
        self.assertSuccess(response)

    def test_get_one_contest_announcement(self):
        id = self.test_create_contest_announcement().data["data"]["id"]
        response = self.client.get("{}?id={}".format(self.url, id))
        self.assertSuccess(response)


class ContestAnnouncementListAPITest(APITestCase):
    def setUp(self):
        self.create_super_admin()
        self.url = self.reverse("contest_announcement_api")

    def create_contest_announcements(self):
        contest_id = self.client.post(self.reverse("contest_admin_api"), data=DEFAULT_CONTEST_DATA).data["data"]["id"]
        url = self.reverse("contest_announcement_admin_api")
        self.client.post(url, data={"title": "test title1", "content": "test content1", "contest_id": contest_id})
        self.client.post(url, data={"title": "test title2", "content": "test content2", "contest_id": contest_id})
        return contest_id

    def test_get_contest_announcement_list(self):
        contest_id = self.create_contest_announcements()
        response = self.client.get(self.url, data={"contest_id": contest_id})
        self.assertSuccess(response)


class ContestRankAPITest(APITestCase):
    def setUp(self):
        self.admin = self.create_admin()
        self.acm_contest = Contest.objects.create(created_by=self.admin, **DEFAULT_CONTEST_DATA)
        self.ranked_user = self.create_user("test", "test123", login=False)
        ContestRank.objects.create(user=self.ranked_user, contest=self.acm_contest)
        self.url = self.reverse("contest_rank_api")
        self.rank_cache_key = f"{CacheKey.contest_rank_cache}:{self.acm_contest.id}"
        cache.delete(self.rank_cache_key)
        self.addCleanup(cache.delete, self.rank_cache_key)

    @mock.patch("contest.views.oj.Submission.objects.filter")
    def test_get_contest_rank(self, submission_filter):
        resp = self.client.get(
            self.url,
            data={"contest_id": self.acm_contest.id, "force_refresh": "1"}
        )
        self.assertSuccess(resp)
        submission_filter.assert_not_called()
        user = resp.data["data"]["results"][0]["user"]
        self.assertIsNotNone(user["team_members"])
        self.assertIsNone(user["upvotes"])
        self.assertIsNone(user["downvotes"])
        self.assertIsNone(user["has_culv_flag"])
        self.assertIsNone(user["hidden"])

    @mock.patch("contest.views.oj.Submission.objects.filter")
    def test_api_key_rank_skips_review_data(self, submission_filter):
        self.admin.open_api = True
        self.admin.open_api_appkey = "test-app-key"
        self.admin.save()
        self.client.logout()

        resp = self.client.get(
            self.url,
            data={
                "contest_id": self.acm_contest.id,
                "limit": 1000,
                "force_refresh": "1",
                "include_review_data": "1"
            },
            HTTP_APPKEY=self.admin.open_api_appkey
        )

        self.assertSuccess(resp)
        submission_filter.assert_not_called()
        user = resp.data["data"]["results"][0]["user"]
        self.assertIsNotNone(user["team_members"])
        self.assertIsNone(user["upvotes"])
        self.assertIsNone(user["downvotes"])
        self.assertIsNone(user["has_culv_flag"])
        self.assertIsNone(user["hidden"])

    def test_review_rank_includes_review_data(self):
        profile = self.ranked_user.userprofile
        profile.upvotes = 2
        profile.downvotes = 1
        profile.hidden = True
        profile.save()

        resp = self.client.get(
            self.url,
            data={
                "contest_id": self.acm_contest.id,
                "force_refresh": "1",
                "include_review_data": "1"
            }
        )

        self.assertSuccess(resp)
        user = resp.data["data"]["results"][0]["user"]
        self.assertEqual(user["upvotes"], 2)
        self.assertEqual(user["downvotes"], 1)
        self.assertFalse(user["has_culv_flag"])
        self.assertTrue(user["hidden"])

    def test_cached_rank_prefetches_user_profiles(self):
        for index in range(2):
            user = self.create_user(f"ranked-{index}", "test123", login=False)
            ContestRank.objects.create(user=user, contest=self.acm_contest)

        # Redis pickles/evaluates querysets. This deliberately mirrors a rank cache
        # populated by the pre-fix code, which selected users but not user profiles.
        stale_cached_rank = ContestRank.objects.filter(
            contest=self.acm_contest,
            user__admin_type=AdminType.REGULAR_USER,
            user__is_disabled=False
        ).select_related("user")
        cache.set(self.rank_cache_key, stale_cached_rank)

        with CaptureQueriesContext(connection) as queries:
            resp = self.client.get(
                self.url,
                data={"contest_id": self.acm_contest.id}
            )

        self.assertSuccess(resp)
        profile_queries = [
            query["sql"] for query in queries.captured_queries
            if '"user_profile"' in query["sql"]
        ]
        bulk_profile_queries = [
            sql for sql in profile_queries
            if '"user_profile"."user_id" IN (' in sql
        ]
        self.assertEqual(len(bulk_profile_queries), 1, profile_queries)
        # At present, the other query loads the requesting admin's profile in the
        # permission check. The bound keeps this O(1) without coupling the test to it.
        self.assertLessEqual(len(profile_queries), 2, profile_queries)
