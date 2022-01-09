<template>
  <div>
    <Panel shadow>
      <div slot="title">
        {{ contest.title }}
      </div>
      <div slot="extra">
        <screen-full
          :height="18"
          :width="18"
          class="screen-full"
        />
        <Poptip
          trigger="hover"
          placement="left-start"
        >
          <Icon
            type="android-settings"
            size="20"
          />
          <div
            id="switches"
            slot="content"
          >
            <p>
              <span>{{ $t('m.Menu') }}</span>
              <i-switch v-model="showMenu" />
            </p>
            <p>
              <span>{{ $t('m.Auto_Refresh') }}(10s)</span>
              <i-switch
                :disabled="refreshDisabled"
                @on-change="handleAutoRefresh"
              />
            </p>
            <p v-if="isContestAdmin">
              <span>{{ $t('m.Team_Members') }}</span>
              <i-switch v-model="showTeamMembers" />
            </p>
            <p>
              <Button
                type="primary"
                size="small"
                @click="downloadRankCSV"
              >
                {{ $t('m.download_csv') }}
              </Button>
            </p>
          </div>
        </Poptip>
      </div>
      <Table
        ref="tableRank"
        :columns="columns"
        :data="dataRank"
        disabled-hover
        :loading="loading"
      />
      <Pagination
        :total="total"
        :page-size.sync="limit"
        :current.sync="page"
        show-sizer
        @on-change="getContestRankData"
        @on-page-size-change="getContestRankData(1)"
      />
    </Panel>
  </div>
</template>
<script>
  import { mapActions } from 'vuex'
  import { types } from '../../../../../store'
  import Pagination from '@oj/components/Pagination'
  import ContestRankMixin from './contestRankMixin'
  import utils from '@/utils/utils'
  import time from '@/utils/time'

  export default {
    name: 'AcmContestRank',
    components: {
      Pagination
    },
    mixins: [ContestRankMixin],
    beforeRouteLeave (to, from, next) {
      this.$store.commit(types.CHANGE_CONTEST_ITEM_VISIBLE, {menu: true})
      next()
    },
    data () {
      return {
        total: 0,
        page: 1,
        contestID: '',
        columns: [
          {
            align: 'center',
            fixed: 'left',
            width: 60,
            render: (h, params) => {
              return h('span', {}, params.index + (this.page - 1) * this.limit + 1)
            }
          },
          {
            title: this.$i18n.t('m.Team_Name'),
            fixed: 'left',
            align: 'center',
            minWidth: 180,
            render: (h, params) => {
              return h('span', {
                style: {
                  display: 'inline-block',
                  'max-width': '150px'
                }
              }, params.row.user.team_name)
            }
          },
          {
            title: this.$i18n.t('m.Total_Score'),
            align: 'center',
            minWidth: 110,
            fixed: 'right',
            render: (h, params) => {
              if (this.isContestAdmin) {
                return h('a', {
                  on: {
                    click: () => {
                      this.$router.push({
                        name: 'contest-submission-list',
                        query: {username: params.row.user.username}
                      })
                    }
                  }
                }, params.row.total_score)
              } else {
                return h('span', {}, params.row.total_score)
              }
            }
          },
          {
            title: this.$i18n.t('m.Last_Submission'),
            align: 'center',
            minWidth: 170,
            fixed: 'right',
            render: (h, params) => {
              if (params.row.last_submission) {
                return h('span', {}, time.utcToLocal(params.row.last_submission))
              } else {
                return h('span', {}, null)
              }
            }
          }
        ],
        dataRank: [],
        options: {
          title: {
            text: this.$i18n.t('m.Top_10_Teams'),
            left: 'center'
          },
          tooltip: {
            trigger: 'axis'
          },
          toolbox: {
            show: true,
            feature: {
              dataView: {show: true, readOnly: true},
              magicType: {show: true, type: ['line', 'bar']},
              saveAsImage: {show: true}
            },
            right: '10%'
          },
          calculable: true,
          xAxis: [
            {
              type: 'category',
              data: ['root'],
              boundaryGap: true,
              axisLabel: {
                interval: 0,
                showMinLabel: true,
                showMaxLabel: true,
                align: 'center',
                formatter: (value, index) => {
                  return utils.breakLongWords(value, 14)
                }
              },
              axisTick: {
                alignWithLabel: true
              }
            }
          ],
          yAxis: [
            {
              type: 'value'
            }
          ],
          series: [
            {
              name: this.$i18n.t('m.Score'),
              type: 'bar',
              barMaxWidth: '80',
              data: [0],
              markPoint: {
                data: [
                  {type: 'max', name: 'max'}
                ]
              }
            }
          ]
        }
      }
    },
    mounted () {
      this.contestID = this.$route.params.contestID
      this.getContestRankData(1)
      if (this.contestProblems.length === 0) {
        this.getContestProblems().then((res) => {
          this.addTableColumns(res.data.data)
        })
      } else {
        this.addTableColumns(this.contestProblems)
      }
    },
    methods: {
      ...mapActions(['getContestProblems']),
      applyToTable (data) {
        // deepcopy
        let dataRank = JSON.parse(JSON.stringify(data))
        // 从submission_info中取出相应的problem_id 放入到父object中,这么做主要是为了适应iview table的data格式
        // 见https://www.iviewui.com/components/table
        dataRank.forEach((rank, i) => {
          let info = rank.submission_info
          Object.keys(info).forEach(problemID => {
            dataRank[i][problemID] = info[problemID]
          })
        })
        this.dataRank = dataRank
      },
      addTableColumns (problems) {
        problems.forEach(problem => {
          this.columns.push({
            align: 'center',
            key: problem.id,
            minWidth: 80,
            renderHeader: (h, params) => {
              return h('a', {
                'class': {
                  'emphasis': true
                },
                on: {
                  click: () => {
                    this.$router.push({
                      name: 'contest-problem-details',
                      params: {
                        contestID: this.contestID,
                        problemID: problem._id
                      }
                    })
                  }
                }
              }, problem._id)
            },
            render: (h, params) => {
              return h('span', params.row[problem.id])
            }
          })
        })
      },
      downloadRankCSV () {
        utils.downloadFile(`contest_rank?download_csv=1&contest_id=${this.$route.params.contestID}&force_refrash=${this.forceUpdate ? '1' : '0'}`)
      }
    }
  }
</script>
<style scoped lang="less">

  .screen-full {
    margin-right: 8px;
  }

  #switches {
    p {
      margin-top: 5px;
      &:first-child {
        margin-top: 0;
      }
      span {
        margin-left: 8px;
      }
    }
  }
</style>
