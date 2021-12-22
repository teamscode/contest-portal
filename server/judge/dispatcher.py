import hashlib
import json
import logging
from urllib.parse import urljoin

import requests
from django.db import transaction, IntegrityError
from django.db.models import F

from account.models import User
from conf.models import JudgeServer
from contest.models import ContestRuleType, ContestRank, ContestStatus
from options.options import SysOptions
from problem.models import Problem
from problem.utils import parse_problem_template
from submission.models import JudgeStatus, Submission
from utils.cache import cache
from utils.constants import CacheKey

logger = logging.getLogger(__name__)


# 继续处理在队列中的问题
def process_pending_task():
    if cache.llen(CacheKey.waiting_queue):
        # 防止循环引入
        from judge.tasks import judge_task
        tmp_data = cache.rpop(CacheKey.waiting_queue)
        if tmp_data:
            data = json.loads(tmp_data.decode("utf-8"))
            judge_task.send(**data)


class ChooseJudgeServer:
    def __init__(self):
        self.server = None

    def __enter__(self) -> [JudgeServer, None]:
        with transaction.atomic():
            servers = JudgeServer.objects.select_for_update().filter(is_disabled=False).order_by("task_number")
            servers = [s for s in servers if s.status == "normal"]
            for server in servers:
                if server.task_number < server.cpu_core:
                    server.task_number = F("task_number") + 1
                    server.save(update_fields=["task_number"])
                    self.server = server
                    return server
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.server:
            JudgeServer.objects.filter(id=self.server.id).update(task_number=F("task_number") - 1)


class DispatcherBase(object):
    def __init__(self):
        self.token = hashlib.sha256(SysOptions.judge_server_token.encode("utf-8")).hexdigest()

    def _request(self, url, data=None):
        kwargs = {"headers": {"X-Judge-Server-Token": self.token}}
        if data:
            kwargs["json"] = data
        try:
            return requests.post(url, **kwargs).json()
        except Exception as e:
            logger.exception(e)


class SPJCompiler(DispatcherBase):
    def __init__(self, spj_code, spj_version, spj_language):
        super().__init__()
        spj_compile_config = list(filter(lambda config: spj_language == config["name"], SysOptions.spj_languages))[0]["spj"][
            "compile"]
        self.data = {
            "src": spj_code,
            "spj_version": spj_version,
            "spj_compile_config": spj_compile_config
        }

    def compile_spj(self):
        with ChooseJudgeServer() as server:
            if not server:
                return "No available judge_server"
            result = self._request(urljoin(server.service_url, "compile_spj"), data=self.data)
            if not result:
                return "Failed to call judge server"
            if result["err"]:
                return result["data"]


class JudgeDispatcher(DispatcherBase):
    def __init__(self, submission_id, problem_id):
        super().__init__()
        self.submission = Submission.objects.get(id=submission_id)
        self.contest_id = self.submission.contest_id
        self.last_result = self.submission.result if self.submission.info else None

        if self.contest_id:
            self.problem = Problem.objects.select_related("contest").get(id=problem_id, contest_id=self.contest_id)
            self.contest = self.problem.contest
        else:
            self.problem = Problem.objects.get(id=problem_id)

    def _compute_statistic_info(self, resp_data):
        # 用时和内存占用保存为多个测试点中最长的那个
        self.submission.statistic_info["time_cost"] = max([x["cpu_time"] for x in resp_data])
        self.submission.statistic_info["memory_cost"] = max([x["memory"] for x in resp_data])

        # sum up the score in OI mode
        score = 0
        try:
            for i in range(len(resp_data)):
                if resp_data[i]["result"] == JudgeStatus.ACCEPTED:
                    resp_data[i]["score"] = self.problem.test_case_score[i]["score"]
                    score += resp_data[i]["score"]
                else:
                    resp_data[i]["score"] = 0
        except IndexError:
            logger.error(f"Index Error raised when summing up the score in problem {self.problem.id}")
            self.submission.statistic_info["score"] = 0
            return
        self.submission.statistic_info["score"] = score

    def judge(self):
        language = self.submission.language
        sub_config = list(filter(lambda item: language == item["name"], SysOptions.languages))[0]
        spj_config = {}
        if self.problem.spj_code:
            for lang in SysOptions.spj_languages:
                if lang["name"] == self.problem.spj_language:
                    spj_config = lang["spj"]
                    break

        if language in self.problem.template:
            template = parse_problem_template(self.problem.template[language])
            code = f"{template['prepend']}\n{self.submission.code}\n{template['append']}"
        else:
            code = self.submission.code

        adjusted_time_limit = self.problem.time_limit
        if sub_config["name"] == "Java":
            adjusted_time_limit *= 2
        elif sub_config["name"] == "Python 2" or sub_config["name"] == "Python 3":
            adjusted_time_limit *= 4

        data = {
            "language_config": sub_config["config"],
            "src": code,
            "max_cpu_time": adjusted_time_limit,
            "max_memory": 1024 * 1024 * self.problem.memory_limit,
            "test_case_id": self.problem.test_case_id,
            "output": False,
            "spj_version": self.problem.spj_version,
            "spj_config": spj_config.get("config"),
            "spj_compile_config": spj_config.get("compile"),
            "spj_src": self.problem.spj_code,
            "io_mode": self.problem.io_mode
        }

        with ChooseJudgeServer() as server:
            if not server:
                data = {"submission_id": self.submission.id, "problem_id": self.problem.id}
                cache.lpush(CacheKey.waiting_queue, json.dumps(data))
                return
            Submission.objects.filter(id=self.submission.id).update(result=JudgeStatus.JUDGING)
            resp = self._request(urljoin(server.service_url, "/judge"), data=data)

        if not resp:
            Submission.objects.filter(id=self.submission.id).update(result=JudgeStatus.SYSTEM_ERROR)
            return

        if resp["err"]:
            self.submission.result = JudgeStatus.COMPILE_ERROR
            self.submission.statistic_info["err_info"] = resp["data"]
            self.submission.statistic_info["score"] = 0
        else:
            resp["data"].sort(key=lambda x: int(x["test_case"]))
            self.submission.info = resp
            self._compute_statistic_info(resp["data"])
            error_test_case = list(filter(lambda case: case["result"] != 0, resp["data"]))
            # OI模式下, 若多个测试点全部正确则AC， 若全部错误则取第一个错误测试点状态，否则为部分正确
            if not error_test_case:
                self.submission.result = JudgeStatus.ACCEPTED
            elif len(error_test_case) == len(resp["data"]):
                self.submission.result = error_test_case[0]["result"]
            else:
                self.submission.result = JudgeStatus.PARTIALLY_ACCEPTED
        self.submission.save()

        if self.contest_id:
            if self.contest.status != ContestStatus.CONTEST_UNDERWAY or \
                    User.objects.get(id=self.submission.user_id).is_contest_admin(self.contest):
                logger.info(
                    "Contest debug mode, id: " + str(self.contest_id) + ", submission id: " + self.submission.id)
                return
            with transaction.atomic():
                self.update_contest_problem_status()
                self.update_contest_rank()
        else:
            if self.last_result:
                self.update_problem_status_rejudge()
            else:
                self.update_problem_status()

        # 至此判题结束，尝试处理任务队列中剩余的任务
        process_pending_task()

    def update_problem_status_rejudge(self):
        result = str(self.submission.result)
        problem_id = str(self.problem.id)
        with transaction.atomic():
            # update problem status
            problem = Problem.objects.select_for_update().get(contest_id=self.contest_id, id=self.problem.id)
            if self.last_result != JudgeStatus.ACCEPTED and self.submission.result == JudgeStatus.ACCEPTED:
                problem.accepted_number += 1
            problem_info = problem.statistic_info
            problem_info[self.last_result] = problem_info.get(self.last_result, 1) - 1
            problem_info[result] = problem_info.get(result, 0) + 1
            problem.save(update_fields=["statistic_info"])

            profile = User.objects.select_for_update().get(id=self.submission.user_id).userprofile
            problems_status = profile.problems_status.get("problems", {})
            score = self.submission.statistic_info["score"]
            if problems_status[problem_id]["status"] != JudgeStatus.ACCEPTED:
                # minus last time score, add this tim score
                problems_status[problem_id]["score"] = score
                problems_status[problem_id]["status"] = self.submission.result
            profile.problems_status["problems"] = problems_status
            profile.save(update_fields=["problems_status"])

    def update_problem_status(self):
        result = str(self.submission.result)
        problem_id = str(self.problem.id)
        with transaction.atomic():
            # update problem status
            problem = Problem.objects.select_for_update().get(contest_id=self.contest_id, id=self.problem.id)
            problem.submission_number += 1
            if self.submission.result == JudgeStatus.ACCEPTED:
                problem.accepted_number += 1
            problem_info = problem.statistic_info
            problem_info[result] = problem_info.get(result, 0) + 1
            problem.save(update_fields=["accepted_number", "submission_number", "statistic_info"])

            # update_userprofile
            user = User.objects.select_for_update().get(id=self.submission.user_id)
            user_profile = user.userprofile
            problems_status = user_profile.problems_status.get("problems", {})
            score = self.submission.statistic_info["score"]
            if problem_id not in problems_status:
                problems_status[problem_id] = {"status": self.submission.result,
                                               "_id": self.problem._id,
                                               "score": score}
            elif problems_status[problem_id]["status"] != JudgeStatus.ACCEPTED:
                # minus last time score, add this time score
                problems_status[problem_id]["score"] = score
                problems_status[problem_id]["status"] = self.submission.result
            user_profile.problems_status["problems"] = problems_status
            user_profile.save(update_fields=["problems_status"])

    def update_contest_problem_status(self):
        with transaction.atomic():
            user = User.objects.select_for_update().get(id=self.submission.user_id)
            user_profile = user.userprofile
            problem_id = str(self.problem.id)
            contest_problems_status = user_profile.problems_status.get("contest_problems", {})
            score = self.submission.statistic_info["score"]
            if problem_id not in contest_problems_status:
                contest_problems_status[problem_id] = {"status": self.submission.result,
                                                       "_id": self.problem._id,
                                                       "score": score}
            elif contest_problems_status[problem_id]["score"] < score:
                contest_problems_status[problem_id]["score"] = score
                contest_problems_status[problem_id]["status"] = self.submission.result
            user_profile.problems_status["contest_problems"] = contest_problems_status
            user_profile.save(update_fields=["problems_status"])

            problem = Problem.objects.select_for_update().get(contest_id=self.contest_id, id=self.problem.id)
            result = str(self.submission.result)
            problem_info = problem.statistic_info
            problem_info[result] = problem_info.get(result, 0) + 1
            problem.submission_number += 1
            if self.submission.result == JudgeStatus.ACCEPTED:
                problem.accepted_number += 1
            problem.save(update_fields=["submission_number", "accepted_number", "statistic_info"])

    def update_contest_rank(self):
        cache.delete(f"{CacheKey.contest_rank_cache}:{self.contest.id}")

        def get_rank(model):
            return model.objects.select_for_update().get(user_id=self.submission.user_id, contest=self.contest)

        model = ContestRank

        try:
            rank = get_rank(model)
        except model.DoesNotExist:
            try:
                model.objects.create(user_id=self.submission.user_id, contest=self.contest)
                rank = get_rank(model)
            except IntegrityError:
                rank = get_rank(model)

        problem_id = str(self.submission.problem_id)
        current_score = self.submission.statistic_info["score"]
        last_score = rank.submission_info.get(problem_id, 0)

        if current_score > last_score:
            rank.total_score = rank.total_score - last_score + current_score
            rank.submission_info[problem_id] = current_score
            rank.last_submission = self.submission.create_time
            rank.save()
