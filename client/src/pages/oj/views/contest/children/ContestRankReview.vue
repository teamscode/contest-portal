<template>
  <div>
    <Panel shadow>
      <div slot="title">
        {{ contest.title }} - {{ $t('m.Review') }}
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
            type="md-settings"
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
            <p>
              <span>Show Hidden Teams</span>
              <i-switch v-model="showHidden" />
            </p>
          </div>
        </Poptip>
      </div>
      <Table
        ref="tableRank"
        :columns="columns"
        :data="visibleDataRank"
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
  import ContestRankMixin from './contestRankMixin'
  import time from '@/utils/time'
  import api from '@oj/api'
  import { getVoteColor, getVoteFill } from './reviewUtils'
  import { types } from '../../../../../store'

  export default {
    name: 'ContestRankReview',
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
            render: (h, { row }) => {
              return h('a', {
                on: {
                  click: () => {
                    this.$router.push({
                      name: 'contest-review-console',
                      params: {contestID: this.contestID, teamId: row.user.id}
                    })
                  }
                }
              }, row.user.team_name)
            }
          },
          {
            title: 'Review',
            align: 'center',
            minWidth: 160,
            render: (h, { row }) => {
              const user = row.user
              const fillPct = Math.round(getVoteFill(user) * 100)
              return h('div', { class: 'lb-vote-bar-outer' }, [
                h('div', { class: 'lb-vote-bar-inner', style: { width: fillPct + '%', backgroundColor: getVoteColor(user) } }),
                h('span', { class: 'lb-vote-bar-label' }, `+${user.upvotes}/-${user.downvotes}${user.has_culv_flag ? ' (culv)' : ''}${user.hidden ? ' (hidden)' : ''}`)
              ])
            }
          },
          {
            title: 'Actions',
            align: 'center',
            minWidth: 260,
            render: (h, { row }) => {
              const userId = row.user.id
              return h('div', { class: 'review-actions-cell' }, [
                h('Button', {
                  props: { size: 'small', type: 'success', icon: 'md-thumbs-up' },
                  on: { click: () => this.vote(userId, 'upvote') }
                }),
                h('Button', {
                  props: { size: 'small', type: 'error', icon: 'md-thumbs-down' },
                  on: { click: () => this.vote(userId, 'downvote') }
                }),
                h('Button', {
                  props: { size: 'small', type: row.user.hidden ? 'default' : 'warning', icon: 'md-eye-off' },
                  on: { click: () => this.toggleHide(row) }
                }, row.user.hidden ? 'Unhide' : 'Hide'),
                h('Button', {
                  props: { size: 'small', icon: 'md-undo', disabled: !(this.undoMap[userId] && this.undoMap[userId].length) },
                  on: { click: () => this.undo(userId) }
                })
              ])
            }
          },
          {
            title: this.$i18n.t('m.Total_Score'),
            align: 'center',
            minWidth: 110,
            fixed: 'right',
            render: (h, params) => {
              return h('span', {}, params.row.total_score)
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
        showHidden: false,
        undoMap: {} // userId -> [{type:'vote', action}, ...]
      }
    },
    computed: {
      refreshDisabled () { return false },
      visibleDataRank () {
        return this.showHidden ? this.dataRank : this.dataRank.filter(row => !row.user.hidden)
      }
    },
    mounted () {
      this.contestID = this.$route.params.contestID
      this.getContestRankData(1)
    },
    methods: {
      applyToTable (data) {
        // deepcopy
        this.dataRank = JSON.parse(JSON.stringify(data))
      },
      findRow (userId) {
        return this.dataRank.find(row => row.user.id === userId)
      },
      applyVoteResult (userId, result) {
        const row = this.findRow(userId)
        if (row) { row.user.upvotes = result.upvotes; row.user.downvotes = result.downvotes }
      },
      applyHideResult (userId, result) {
        const row = this.findRow(userId)
        if (row) { row.user.hidden = result.hidden }
      },
      pushUndo (userId, entry) {
        const stack = this.undoMap[userId] || []
        stack.push(entry)
        this.$set(this.undoMap, userId, stack)
      },
      vote (userId, action) {
        api.teamReviewAction({ contest_id: this.contestID, user_id: userId, action, delta: 1 }).then(res => {
          this.applyVoteResult(userId, res.data.data)
          this.pushUndo(userId, { type: 'vote', action })
        })
      },
      toggleHide (row) {
        const userId = row.user.id
        const next = row.user.hidden ? 'unhide' : 'hide'
        api.teamReviewAction({ contest_id: this.contestID, user_id: userId, action: next }).then(res => {
          this.applyHideResult(userId, res.data.data)
        })
      },
      undo (userId) {
        const stack = this.undoMap[userId]
        if (!stack || !stack.length) return
        const last = stack.pop()
        api.teamReviewAction({ contest_id: this.contestID, user_id: userId, action: last.action, delta: -1 })
          .then(res => this.applyVoteResult(userId, res.data.data))
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
<!--
  NOT scoped on purpose: this component's Review/Actions table columns are built via
  iView Table's `render(h, params)` callback, whose `h` belongs to the Table component's
  own render context -- Vue's scoped-CSS data-v-* attribute never gets attached to those
  vnodes, so a `scoped` block here would silently never match them.
-->
<style lang="less">
  .lb-vote-bar-outer {
    position: relative;
    width: 100%;
    height: 22px;
    border-radius: 3px;
    background: #f0f0f0;
    border: 1px solid #dcdee2;
    overflow: hidden;
  }

  .lb-vote-bar-inner {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    transition: width 0.2s ease;
  }

  .lb-vote-bar-label {
    position: relative;
    z-index: 1;
    display: block;
    font-size: 12px;
    font-weight: 600;
    line-height: 22px;
    white-space: nowrap;
    color: #1c2438;
    text-shadow: 0 0 3px rgba(255, 255, 255, 0.85), 0 0 3px rgba(255, 255, 255, 0.85);
  }

  .review-actions-cell {
    display: flex;
    justify-content: center;
    gap: 4px;
    flex-wrap: wrap;
  }
</style>
