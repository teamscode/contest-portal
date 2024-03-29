<template>
  <div class="flex-container">
    <div id="problem-main">
      <!--problem main-->
      <Panel
        :padding="40"
        shadow
      >
        <div slot="title">
          {{ problem.title }}
        </div>
        <div
          id="problem-content"
          v-katex
          class="markdown-body"
        >
          <p class="title">
            {{ $t('m.Description') }}
          </p>
          <p
            class="content"
            v-html="problem.description"
          />
          <!-- {{$t('m.music')}} -->
          <p class="title">
            {{ $t('m.Input') }} <span v-if="problem.io_mode.io_mode=='File IO'">({{ $t('m.FromFile') }}: {{ problem.io_mode.input }})</span>
          </p>
          <p
            class="content"
            v-html="problem.input_description"
          />

          <p class="title">
            {{ $t('m.Output') }} <span v-if="problem.io_mode.io_mode=='File IO'">({{ $t('m.ToFile') }}: {{ problem.io_mode.output }})</span>
          </p>
          <p
            class="content"
            v-html="problem.output_description"
          />

          <div
            v-for="(sample, index) of problem.samples"
            :key="index"
          >
            <div class="flex-container sample">
              <div class="sample-input">
                <p class="title">
                  {{ $t('m.Sample_Input') }} {{ index + 1 }}
                  <a
                    v-clipboard:copy="sample.input"
                    v-clipboard:success="onCopy"
                    v-clipboard:error="onCopyError"
                    class="copy"
                  >
                    <Icon type="md-clipboard" />
                  </a>
                </p>
                <pre>{{ sample.input }}</pre>
              </div>
              <div class="sample-output">
                <p class="title">
                  {{ $t('m.Sample_Output') }} {{ index + 1 }}
                </p>
                <pre>{{ sample.output }}</pre>
              </div>
            </div>
          </div>

          <div v-if="problem.hint">
            <p class="title">
              {{ $t('m.Hint') }}
            </p>
            <p
              class="content"
              v-html="problem.hint"
            />
          </div>

          <div v-if="problem.source">
            <p class="title">
              {{ $t('m.Source') }}
            </p>
            <p class="content">
              {{ problem.source }}
            </p>
          </div>
        </div>
      </Panel>
      <!--problem main end-->
      <Card
        id="submit-code"
        :padding="20"
        dis-hover
      >
        <CodeMirror
          :value.sync="code"
          :languages="problem.languages"
          :language="language"
          :theme="theme"
          @resetCode="onResetToTemplate"
          @changeTheme="onChangeTheme"
          @changeLang="onChangeLang"
        />
        <Row
          type="flex"
          justify="space-between"
        >
          <Col :span="10">
            <div
              v-if="statusVisible"
              class="status"
            >
              <template>
                <span>{{ $t('m.Status') }}</span>
                <Tag
                  type="dot"
                  :color="submissionStatus.color"
                  @click.native="handleRoute('/status/'+submissionId)"
                >
                  {{ $t('m.' + submissionStatus.text.replace(/ /g, "_")) }}
                </Tag>
              </template>
            </div>
            <div v-else-if="problem.my_status === 0">
              <Alert
                type="success"
                show-icon
              >
                {{ $t('m.You_have_solved_the_problem') }}
              </Alert>
            </div>
            <div v-if="contestEnded">
              <Alert
                type="warning"
                show-icon
              >
                {{ $t('m.Contest_has_ended') }}
              </Alert>
            </div>
          </Col>

          <Col :span="12">
            <template v-if="captchaRequired">
              <div class="captcha-container">
                <Tooltip
                  v-if="captchaRequired"
                  content="Click to refresh"
                  placement="top"
                >
                  <img
                    :src="captchaSrc"
                    @click="getCaptchaSrc"
                  >
                </Tooltip>
                <Input
                  v-model="captchaCode"
                  class="captcha-code"
                />
              </div>
            </template>
            <Button
              type="warning"
              icon="md-create"
              :loading="submitting"
              :disabled="problemSubmitDisabled || submitted"
              class="fl-right"
              @click="submitCode"
            >
              <span v-if="submitting">{{ $t('m.Submitting') }}</span>
              <span v-else>{{ $t('m.Submit') }}</span>
            </Button>
          </Col>
        </Row>
      </Card>
    </div>

    <div id="right-column">
      <VerticalMenu @on-click="handleRoute">
        <template v-if="contestID">
          <VerticalMenu-item :route="{name: 'contest-problem-list', params: {contestID: contestID}}">
            <Icon type="ios-photos" />
            {{ $t('m.Problems') }}
          </VerticalMenu-item>
        </template>

        <VerticalMenu-item
          :route="submissionRoute"
        >
          <Icon type="md-list" />
          {{ $t('m.Submissions') }}
        </VerticalMenu-item>

        <template v-if="contestID">
          <VerticalMenu-item
            v-if="!contestID || OIContestRealTimePermission"
            :route="{name: 'contest-rank', params: {contestID: contestID}}"
          >
            <Icon type="ios-stats" />
            {{ $t('m.Rankings') }}
          </VerticalMenu-item>
          <VerticalMenu-item :route="{name: 'contest-details', params: {contestID: contestID}}">
            <Icon type="md-home" />
            {{ $t('m.View_Contest') }}
          </VerticalMenu-item>
        </template>
      </VerticalMenu>

      <Card id="info">
        <div
          slot="title"
          class="header"
        >
          <Icon type="md-information-circle" />
          <span class="card-title">Limits</span>
        </div>
        <ul>
          <li>
            <p>C/C++</p>
            <p>{{ problem.time_limit }} ms</p>
          </li>
          <li>
            <p>Java</p>
            <p>{{ problem.time_limit*2 }} ms</p>
          </li>
          <li>
            <p>Python</p>
            <p>{{ problem.time_limit*4 }} ms</p>
          </li>
          <li>
            <p>{{ $t('m.Memory_Limit') }}</p>
            <p>{{ problem.memory_limit }} MB</p>
          </li>
        </ul>
      </Card>
      <Card id="info">
        <div
          slot="title"
          class="header"
        >
          <Icon type="md-information-circle" />
          <span class="card-title">{{ $t('m.Information') }}</span>
        </div>
        <ul>
          <li>
            <p>ID</p>
            <p>{{ problem._id }}</p>
          </li>
          <li>
            <p>{{ $t('m.IOMode') }}</p>
            <p>{{ problem.io_mode.io_mode }}</p>
          </li>
          <li>
            <p>{{ $t('m.Created') }}</p>
            <p>{{ problem.created_by.username }}</p>
          </li>
          <li v-if="problem.difficulty">
            <p>{{ $t('m.Level') }}</p>
            <p>{{ $t('m.' + problem.difficulty) }}</p>
          </li>
          <li v-if="problem.total_score">
            <p>{{ $t('m.Score') }}</p>
            <p>{{ problem.total_score }}</p>
          </li>
          <li>
            <p>{{ $t('m.Tags') }}</p>
            <p>
              <Poptip
                trigger="hover"
                placement="left-end"
              >
                <a>{{ $t('m.Show') }}</a>
                <div slot="content">
                  <Tag
                    v-for="tag in problem.tags"
                    :key="tag"
                  >
                    {{ tag }}
                  </Tag>
                </div>
              </Poptip>
            </p>
          </li>
        </ul>
      </Card>
    </div>
  </div>
</template>

<script>
  import {mapGetters, mapActions} from 'vuex'
  import {types} from '../../../../store'
  import CodeMirror from '@oj/components/CodeMirror.vue'
  import storage from '@/utils/storage'
  import {FormMixin} from '@oj/components/mixins'
  import {JUDGE_STATUS, CONTEST_STATUS, buildProblemCodeKey} from '@/utils/constants'
  import api from '@oj/api'

  export default {
    name: 'Problem',
    components: {
      CodeMirror
    },
    mixins: [FormMixin],
    beforeRouteEnter (to, from, next) {
      let problemCode = storage.get(buildProblemCodeKey(to.params.problemID, to.params.contestID))
      if (problemCode) {
        next(vm => {
          vm.language = problemCode.language
          vm.code = problemCode.code
          vm.theme = problemCode.theme
        })
      } else {
        next()
      }
    },
    data () {
      return {
        statusVisible: false,
        captchaRequired: false,
        submissionExists: false,
        captchaCode: '',
        captchaSrc: '',
        contestID: '',
        problemID: '',
        submitting: false,
        code: '',
        language: 'C++17',
        theme: 'solarized',
        submissionId: '',
        submitted: false,
        result: {
          result: 9
        },
        problem: {
          title: '',
          description: '',
          hint: '',
          my_status: '',
          template: {},
          languages: [],
          created_by: {
            username: ''
          },
          tags: [],
          io_mode: {'io_mode': 'Standard IO'}
        }
      }
    },
    mounted () {
      this.$store.commit(types.CHANGE_CONTEST_ITEM_VISIBLE, {menu: false})
      this.init()
    },
    methods: {
      ...mapActions(['changeDomTitle']),
      init () {
        this.$Loading.start()
        this.contestID = this.$route.params.contestID
        this.problemID = this.$route.params.problemID
        let func = this.$route.name === 'problem-details' ? 'getProblem' : 'getContestProblem'
        api[func](this.problemID, this.contestID).then(res => {
          this.$Loading.finish()
          let problem = res.data.data
          this.changeDomTitle({title: problem.title})
          api.submissionExists(problem.id).then(res => {
            this.submissionExists = res.data.data
          })
          this.problem = problem

          // 在beforeRouteEnter中修改了, 说明本地有code，无需加载template
          if (this.code !== '') {
            return
          }
          // try to load problem template
          if (this.problem.languages.includes('C++17')) {
            this.language = 'C++17'
          } else if (this.problem.languages.includes('C++11')) {
            this.language = 'C++11'
          } else if (this.problem.languages.includes('Java')) {
            this.language = 'Java'
          } else if (this.problem.languages.includes('Python 3')) {
            this.language = 'Python 3'
          } else if (this.problem.languages.includes('Python 2')) {
            this.language = 'Python 2'
          } else {
            this.language = this.probelm.languages[0]
          }
          let template = this.problem.template
          if (template && template[this.language]) {
            this.code = template[this.language]
          }
        }, () => {
          this.$Loading.error()
        })
      },
      handleRoute (route) {
        this.$router.push(route)
      },
      onChangeLang (newLang) {
        if (this.problem.template[newLang]) {
          if (this.code.trim() === '') {
            this.code = this.problem.template[newLang]
          }
        }
        this.language = newLang
      },
      onChangeTheme (newTheme) {
        this.theme = newTheme
      },
      onResetToTemplate () {
        this.$Modal.confirm({
          content: this.$i18n.t('m.Are_you_sure_you_want_to_reset_your_code'),
          onOk: () => {
            let template = this.problem.template
            if (template && template[this.language]) {
              this.code = template[this.language]
            } else {
              this.code = ''
            }
          }
        })
      },
      checkSubmissionStatus () {
        // 使用setTimeout避免一些问题
        if (this.refreshStatus) {
          // 如果之前的提交状态检查还没有停止,则停止,否则将会失去timeout的引用造成无限请求
          clearTimeout(this.refreshStatus)
        }
        const checkStatus = () => {
          let id = this.submissionId
          api.getSubmission(id).then(res => {
            this.result = res.data.data
            if (Object.keys(res.data.data.statistic_info).length !== 0) {
              this.submitting = false
              this.submitted = false
              clearTimeout(this.refreshStatus)
              this.init()
            } else {
              this.refreshStatus = setTimeout(checkStatus, 2000)
            }
          }, res => {
            this.submitting = false
            clearTimeout(this.refreshStatus)
          })
        }
        this.refreshStatus = setTimeout(checkStatus, 2000)
      },
      submitCode () {
        if (this.code.trim() === '') {
          this.$error(this.$i18n.t('m.Code_can_not_be_empty'))
          return
        }
        this.submissionId = ''
        this.result = {result: 9}
        this.submitting = true
        let data = {
          problem_id: this.problem.id,
          language: this.language,
          code: this.code,
          contest_id: this.contestID
        }
        if (this.captchaRequired) {
          data.captcha = this.captchaCode
        }
        const submitFunc = (data, detailsVisible) => {
          this.statusVisible = true
          api.submitCode(data).then(res => {
            this.submissionId = res.data.data && res.data.data.submission_id
            // 定时检查状态
            this.submitting = false
            this.submissionExists = true
            if (!detailsVisible) {
              this.$Modal.success({
                title: this.$i18n.t('m.Success'),
                content: this.$i18n.t('m.Submit_code_successfully')
              })
              return
            }
            this.submitted = true
            this.checkSubmissionStatus()
          }, res => {
            this.getCaptchaSrc()
            if (res.data.data.startsWith('Captcha is required')) {
              this.captchaRequired = true
            }
            this.submitting = false
            this.statusVisible = false
          })
        }

        submitFunc(data, true)
      },
      onCopy (event) {
        this.$success('Copied!')
      },
      onCopyError (e) {
        this.$error('Failed to copy')
      }
    },
    computed: {
      ...mapGetters(['problemSubmitDisabled', 'OIContestRealTimePermission', 'contestStatus']),
      contest () {
        return this.$store.state.contest.contest
      },
      contestEnded () {
        return this.contestStatus === CONTEST_STATUS.ENDED
      },
      submissionStatus () {
        return {
          text: JUDGE_STATUS[this.result.result]['name'],
          color: JUDGE_STATUS[this.result.result]['color']
        }
      },
      submissionRoute () {
        if (this.contestID) {
          return {name: 'contest-submission-list', query: {problemID: this.problemID}}
        } else {
          return {name: 'submission-list', query: {problemID: this.problemID}}
        }
      }
    },
    beforeRouteLeave (to, from, next) {
      // 防止切换组件后仍然不断请求
      clearInterval(this.refreshStatus)

      this.$store.commit(types.CHANGE_CONTEST_ITEM_VISIBLE, {menu: true})
      storage.set(buildProblemCodeKey(this.problem._id, from.params.contestID), {
        code: this.code,
        language: this.language,
        theme: this.theme
      })
      next()
    },
    watch: {
      '$route' () {
        this.init()
      }
    }
  }
</script>

<style lang="less" scoped>
  .card-title {
    margin-left: 8px;
  }

  .flex-container {
    #problem-main {
      flex: auto;
      margin-right: 18px;
    }
    #right-column {
      flex: none;
      width: 220px;
    }
  }

  #problem-content {
    margin-top: -50px;
    .title {
      font-size: 20px;
      font-weight: 400;
      margin: 25px 0 8px 0;
      color: #3091f2;
      .copy {
        padding-left: 8px;
      }
    }
    p.content {
      margin-left: 25px;
      margin-right: 20px;
      font-size: 15px;
      color: rgb(51, 51, 51);
    }
    .sample {
      align-items: stretch;
      &-input, &-output {
        width: 50%;
        flex: 1 1 auto;
        display: flex;
        flex-direction: column;
        margin-right: 5%;
      }
      pre {
        flex: 1 1 auto;
        align-self: stretch;
        border-style: solid;
        background: transparent;
      }
    }
  }

  #submit-code {
    margin-top: 20px;
    margin-bottom: 20px;
    .status {
      float: left;
      span {
        margin-right: 10px;
        margin-left: 10px;
      }
    }
    .captcha-container {
      display: inline-block;
      .captcha-code {
        width: auto;
        margin-top: -20px;
        margin-left: 20px;
      }
    }
  }

  #info {
    margin-bottom: 20px;
    margin-top: 20px;
    ul {
      list-style-type: none;
      li {
        border-bottom: 1px dotted #e9eaec;
        margin-bottom: 10px;
        p {
          display: inline-block;
        }
        p:first-child {
          width: 90px;
        }
        p:last-child {
          float: right;
        }
      }
    }
  }

  .fl-right {
    float: right;
  }
</style>

