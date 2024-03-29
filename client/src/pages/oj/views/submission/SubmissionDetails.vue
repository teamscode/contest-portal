<template>
  <div style="margin-bottom: 20px">
    <Row
      type="flex"
      justify="space-around"
    >
      <Col
        id="status"
        :span="20"
      >
        <Alert
          :type="status.type"
          v-if="status.statusName==='Submitting'||status.statusName==='Pending'||status.statusName==='Judging'"
          show-icon
        >
          <span class="title">{{ $t('m.' + status.statusName.replace(/ /g, "_")) }}</span>
          <div
            slot="desc"
            class="content"
          >
            <template>
              <span>{{ $t('m.Lang') }}: {{ submission.language }}</span>
              <span>{{ $t('m.Author') }}: {{ submission.username }}</span>
            </template>
          </div>
        </Alert>
        <Alert
          :type="status.type"
          v-else
          show-icon
        >
          <span class="title">{{ $t('m.' + status.statusName.replace(/ /g, "_")) }}</span>
          <div
            slot="desc"
            class="content"
          >
            <template v-if="isCE">
              <pre>{{ submission.statistic_info.err_info }}</pre>
            </template>
            <template v-else>
              <span>{{ $t('m.Time') }}: {{ submission.statistic_info.time_cost | submissionTime }}</span>
              <span>{{ $t('m.Memory') }}: {{ submission.statistic_info.memory_cost | submissionMemory }}</span>
              <span>{{ $t('m.Lang') }}: {{ submission.language }}</span>
              <span>{{ $t('m.Author') }}: {{ submission.username }}</span>
            </template>
          </div>
        </Alert>
      </Col>

      <!--后台返info就显示出来， 权限控制放后台 -->
      <Col
        v-if="submission.info && !isCE"
        :span="20"
      >
        <Table
          stripe
          :loading="loading"
          :disabled-hover="true"
          :columns="columns"
          :data="submission.info.data"
        />
      </Col>

      <Col :span="20">
        <Highlight
          :code="submission.code"
          :language="submissionLanguage"
          :border-color="status.highlight"
        />
      </Col>
      <Col
        v-if="submission.can_unshare"
        :span="20"
      >
        <div id="share-btn">
          <Button
            v-if="submission.shared"
            type="warning"
            size="large"
            @click="shareSubmission(false)"
          >
            {{ $t('m.UnShare') }}
          </Button>
          <Button
            v-else
            type="primary"
            size="large"
            @click="shareSubmission(true)"
          >
            {{ $t('m.Share') }}
          </Button>
        </div>
      </Col>
    </Row>
  </div>
</template>

<script>
  import api from '@oj/api'
  import {JUDGE_STATUS} from '@/utils/constants'
  import utils from '@/utils/utils'
  import Highlight from '@/pages/oj/components/Highlight'

  export default {
    name: 'SubmissionDetails',
    components: {
      Highlight
    },
    data () {
      return {
        columns: [
          {
            title: this.$i18n.t('m.ID'),
            align: 'center',
            type: 'index'
          },
          {
            title: this.$i18n.t('m.Status'),
            align: 'center',
            render: (h, params) => {
              return h('Tag', {
                props: {
                  color: JUDGE_STATUS[params.row.result].color
                }
              }, this.$i18n.t('m.' + JUDGE_STATUS[params.row.result].name.replace(/ /g, '_')))
            }
          },
          {
            title: this.$i18n.t('m.Memory'),
            align: 'center',
            render: (h, params) => {
              return h('span', utils.submissionMemoryFormat(params.row.memory))
            }
          },
          {
            title: this.$i18n.t('m.Time'),
            align: 'center',
            render: (h, params) => {
              return h('span', utils.submissionTimeFormat(params.row.cpu_time))
            }
          }
        ],
        submission: {
          result: '6',
          code: '',
          info: {
            data: []
          },
          statistic_info: {
            time_cost: '',
            memory_cost: ''
          }
        },
        isConcat: false,
        loading: false,
        statusChecker: null
      }
    },
    computed: {
      status () {
        return {
          type: JUDGE_STATUS[this.submission.result].type,
          statusName: JUDGE_STATUS[this.submission.result].name,
          color: JUDGE_STATUS[this.submission.result].color,
          highlight: JUDGE_STATUS[this.submission.result].highlight
        }
      },
      submissionLanguage () {
        if (this.submission.language === 'Python 2' || this.submission.language === 'Python 3') {
          return 'Python'
        } else {
          return this.submission.language
        }
      },
      isCE () {
        return this.submission.result === -2
      },
      isAdminRole () {
        return this.$store.getters.isAdminRole
      }
    },
    mounted () {
      this.getSubmission()
      this.statusChecker = setInterval(() => { this.getSubmission() }, 1000)
    },
    beforeDestroy () {
      clearInterval(this.statusChecker)
    },
    methods: {
      getSubmission () {
        this.loading = true
        api.getSubmission(this.$route.params.id).then(res => {
          let data = res.data.data
          if (data.info && data.info.data && !this.isConcat) {
            // score exist means the submission is OI problem submission
            if (data.info.data[0].score !== undefined) {
              this.isConcat = true
              const scoreColumn = {
                title: this.$i18n.t('m.Score'),
                align: 'center',
                key: 'score'
              }
              this.columns.push(scoreColumn)
              this.loadingTable = false
            }
            if (this.isAdminRole) {
              this.isConcat = true
              const adminColumn = [
                {
                  title: this.$i18n.t('m.Real_Time'),
                  align: 'center',
                  render: (h, params) => {
                    return h('span', utils.submissionTimeFormat(params.row.real_time))
                  }
                },
                {
                  title: this.$i18n.t('m.Signal'),
                  align: 'center',
                  key: 'signal'
                }
              ]
              this.columns = this.columns.concat(adminColumn)
            }
          }
          if (data.result !== 6 && data.result !== 7 && data.result !== 9) {
            console.log(data.result)
            this.loading = false
            clearInterval(this.statusChecker)
          }
          this.submission = data
        }, () => {
          clearInterval(this.statusChecker)
          this.loading = false
        })
      },
      shareSubmission (shared) {
        let data = {id: this.submission.id, shared: shared}
        api.updateSubmission(data).then(res => {
          this.getSubmission()
          this.$success(this.$i18n.t('m.Succeeded'))
        }, () => {
        })
      }
    }
  }
</script>

<style scoped lang="less">
  #status {
    .title {
      font-size: 20px;
    }
    .content {
      margin-top: 10px;
      font-size: 14px;
      span {
        margin-right: 10px;
      }
      pre {
        white-space: pre-wrap;
        word-wrap: normal;
        word-break: normal;
      }
    }
  }

  .admin-info {
    margin: 5px 0;
    &-content {
      font-size: 16px;
      padding: 10px;
    }
  }

  #share-btn {
    float: right;
    margin-top: 5px;
    margin-right: 10px;
  }

  pre {
    border: none;
    background: none;
  }
</style>
