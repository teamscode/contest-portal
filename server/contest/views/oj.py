import io

import xlsxwriter
from django.http import HttpResponse
from django.utils.timezone import now
from django.core.cache import cache
from django.db.models import Q

from problem.models import Problem
from utils.api import APIView, validate_serializer
from utils.constants import CacheKey, CONTEST_PASSWORD_SESSION_KEY
from utils.shortcuts import datetime2str, check_is_id
from account.models import AdminType
from account.decorators import login_required, check_contest_permission, check_contest_password

from utils.constants import ContestRuleType, ContestStatus
from ..models import ContestAnnouncement, Contest, ContestRank
from ..serializers import ContestAnnouncementSerializer
from ..serializers import ContestSerializer, ContestPasswordVerifySerializer
from ..serializers import ContestRankSerializer


class ContestAnnouncementListAPI(APIView):
    @check_contest_permission(check_type="announcements")
    def get(self, request):
        contest_id = request.GET.get("contest_id")
        if not contest_id:
            return self.error("Invalid parameter, contest_id is required")
        data = ContestAnnouncement.objects.select_related("created_by").filter(contest_id=contest_id, visible=True)
        max_id = request.GET.get("max_id")
        if max_id:
            data = data.filter(id__gt=max_id)
        return self.success(ContestAnnouncementSerializer(data, many=True).data)


class ContestAPI(APIView):
    def get(self, request):
        id = request.GET.get("id")
        if not id or not check_is_id(id):
            return self.error("Invalid parameter, id is required")
        try:
            contest = Contest.objects.get(id=id, visible=True)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
        data = ContestSerializer(contest).data
        data["now"] = datetime2str(now())
        return self.success(data)


class ContestListAPI(APIView):
    @login_required
    def get(self, request):
        contests = Contest.objects.select_related("created_by").filter(visible=True)
        keyword = request.GET.get("keyword")
        status = request.GET.get("status")
        if keyword:
            contests = contests.filter(title__contains=keyword)
        if status:
            cur = now()
            if status == ContestStatus.CONTEST_NOT_START:
                contests = contests.filter(start_time__gt=cur)
            elif status == ContestStatus.CONTEST_ENDED:
                contests = contests.filter(end_time__lt=cur)
            else:
                contests = contests.filter(start_time__lte=cur, end_time__gte=cur)

        user_profile = request.user.userprofile
        if request.user.is_tester():
            contests = contests.filter(Q(division="Testing") | Q(division="All"))
        elif not request.user.is_admin_role():
            contests = contests.filter(Q(division=getattr(user_profile, "division")) | Q(division="All"))

        return self.success(self.paginate_data(request, contests, ContestSerializer))


class ContestPasswordVerifyAPI(APIView):
    @validate_serializer(ContestPasswordVerifySerializer)
    @login_required
    def post(self, request):
        data = request.data
        try:
            contest = Contest.objects.get(id=data["contest_id"], visible=True, password__isnull=False)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
        if not check_contest_password(data["password"], contest.password):
            return self.error("Wrong password or password expired")

        # password verify OK.
        if CONTEST_PASSWORD_SESSION_KEY not in request.session:
            request.session[CONTEST_PASSWORD_SESSION_KEY] = {}
        request.session[CONTEST_PASSWORD_SESSION_KEY][contest.id] = data["password"]
        # https://docs.djangoproject.com/en/dev/topics/http/sessions/#when-sessions-are-saved
        request.session.modified = True
        return self.success(True)


class ContestAccessAPI(APIView):
    @login_required
    def get(self, request):
        contest_id = request.GET.get("contest_id")
        if not contest_id:
            return self.error()
        try:
            contest = Contest.objects.get(id=contest_id, visible=True, password__isnull=False)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
        session_pass = request.session.get(CONTEST_PASSWORD_SESSION_KEY, {}).get(contest.id)
        return self.success({"access": check_contest_password(session_pass, contest.password)})


class ContestRankAPI(APIView):
    def get_rank(self):
        if self.contest.division == "Testing":
            return ContestRank.objects.filter(contest=self.contest,
                                              user__is_disabled=False). \
                select_related("user").order_by("-total_score", "last_submission")
        else:
            return ContestRank.objects.filter(contest=self.contest,
                                              user__admin_type=AdminType.REGULAR_USER,
                                              user__is_disabled=False). \
                select_related("user").order_by("-total_score", "last_submission")

    def column_string(self, n):
        string = ""
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            string = chr(65 + remainder) + string
        return string

    @check_contest_permission(check_type="ranks")
    def get(self, request):
        download_csv = request.GET.get("download_csv")
        force_refresh = request.GET.get("force_refresh")
        is_contest_admin = request.user.is_authenticated and request.user.is_contest_admin(self.contest)
        serializer = ContestRankSerializer

        if force_refresh == "1" and is_contest_admin:
            qs = self.get_rank()
        else:
            cache_key = f"{CacheKey.contest_rank_cache}:{self.contest.id}"
            qs = cache.get(cache_key)
            if not qs:
                qs = self.get_rank()
                cache.set(cache_key, qs)

        if download_csv and request.user.is_contest_admin(self.contest):
            data = serializer(qs, many=True, is_contest_admin=is_contest_admin).data
            contest_problems = Problem.objects.filter(contest=self.contest, visible=True).order_by("_id")
            problem_ids = [item.id for item in contest_problems]

            f = io.BytesIO()
            workbook = xlsxwriter.Workbook(f)
            worksheet = workbook.add_worksheet()
            worksheet.write("A1", "User ID")
            worksheet.write("B1", "Team Name")
            worksheet.write("C1", "Team Members")

            worksheet.write("D1", "Total Score")
            worksheet.write("E1", "Last Submission")
            for item in range(contest_problems.count()):
                worksheet.write(self.column_string(5 + item) + "1", f"{contest_problems[item].title}")
            for index, item in enumerate(data):
                serialized_team_members = ""
                for member in item["user"]["team_members"]:
                    serialized_team_members += member["name"]
                    serialized_team_members += ";"
                    serialized_team_members += member["email"]
                    serialized_team_members += ";"
                    # convert
                    serialized_team_members += str(member["year"])
                    serialized_team_members += ";"
                    serialized_team_members += member["parent_email"]
                    serialized_team_members += ";"
                worksheet.write_string(index + 1, 0, str(item["user"]["id"]))
                worksheet.write_string(index + 1, 1, item["user"]["team_name"])
                worksheet.write_string(index + 1, 2, serialized_team_members)
                worksheet.write_string(index + 1, 3, str(item["total_score"]))
                worksheet.write_string(index + 1, 4, str(item["last_submission"]))
                for k, v in item["submission_info"].items():
                    worksheet.write_string(index + 1, 4 + problem_ids.index(int(k)), str(v))

            workbook.close()
            f.seek(0)
            response = HttpResponse(f.read())
            response["Content-Disposition"] = f"attachment; filename=content-{self.contest.id}-rank.xlsx"
            response["Content-Type"] = "application/xlsx"
            return response

        page_qs = self.paginate_data(request, qs)
        page_qs["results"] = serializer(page_qs["results"], many=True, is_contest_admin=is_contest_admin).data
        return self.success(page_qs)
