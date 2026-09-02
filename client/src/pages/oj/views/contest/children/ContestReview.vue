<template>
  <div class="flex-container review-container">
    <div class="review-code-pane">
      <div
        v-if="currentSubmission"
        class="review-actions"
      >
        <span class="review-actions-label">{{ currentSubmission.username }}</span>
        <span
          v-if="currentTeamRow"
          class="review-actions-status"
        >+{{ currentTeamRow.user.upvotes }}/-{{ currentTeamRow.user.downvotes }}{{ currentTeamRow.user.has_culv_flag ? ' (culv)' : '' }}{{ currentTeamRow.user.hidden ? ' • Hidden' : '' }}</span>
        <Button
          type="success"
          icon="md-thumbs-up"
          @click="vote('upvote')"
        >
          Upvote
        </Button>
        <Button
          type="error"
          icon="md-thumbs-down"
          @click="vote('downvote')"
        >
          Downvote
        </Button>
        <Button
          :type="currentTeamHidden ? 'default' : 'warning'"
          icon="md-eye-off"
          @click="toggleHide"
        >
          {{ currentTeamHidden ? 'Unhide' : 'Hide' }}
        </Button>
        <Button
          icon="md-undo"
          :disabled="!undoStack.length"
          @click="undo"
        >
          Undo
        </Button>
      </div>
      <Highlight
        v-if="currentSubmission"
        :code="currentCode"
        :language="currentLanguage"
      />
      <p v-else>
        Select a submission below to view its code.
      </p>
    </div>
    <div class="review-side-pane">
      <div class="review-mini-rank">
        <div class="review-mini-rank-header">
          <Button
            size="small"
            :type="activeTeamId === null ? 'primary' : 'default'"
            @click="showAllUsers"
          >
            {{ activeTeamId === null && lastTeamId !== null ? 'Back to Team' : 'Show All Submissions' }}
          </Button>
          <span class="show-hidden-toggle">
            <i-switch
              v-model="showHidden"
              size="small"
            />
            <span>Show Hidden Teams</span>
          </span>
        </div>
        <div class="review-mini-rank-rows">
          <div
            v-for="row in visibleRankRows"
            :key="row.user.id"
            class="review-rank-row"
            :class="{active: row.user.id === activeTeamId, 'is-hidden': row.user.hidden}"
            @click="selectTeam(row.user.id)"
          >
            <div class="vote-bar-outer">
              <div
                class="vote-bar-inner"
                :style="{width: Math.round(getVoteFill(row.user) * 100) + '%', backgroundColor: getVoteColor(row.user)}"
              />
              <span class="vote-bar-name">
                <Icon
                  v-if="row.user.hidden"
                  type="md-eye-off"
                  class="hidden-icon"
                />
                {{ row.user.team_name }}
              </span>
              <span class="vote-bar-label">+{{ row.user.upvotes }}/-{{ row.user.downvotes }}{{ row.user.has_culv_flag ? ' (culv)' : '' }}{{ row.user.hidden ? ' • Hidden' : '' }}</span>
            </div>
          </div>
        </div>
      </div>
      <div
        ref="feedContainer"
        class="review-feed"
        @scroll="onFeedScroll"
      >
        <div
          v-for="item in displayFeed"
          :key="item.sub.id"
          :data-feed-index="item.i"
          class="review-feed-row"
          :class="{active: item.i === selectedIndex}"
          @click="selectSubmission(item.i)"
        >
          <span class="feed-username">{{ item.sub.username }}</span>
          <span class="feed-problem">{{ item.sub.problem }}</span>
          <span
            class="feed-verdict"
            :style="{color: verdictColor(item.sub.result)}"
          >{{ verdictLabel(item.sub.result) }}</span>
          <span class="feed-score">{{ submissionScore(item.sub) }}</span>
          <span class="feed-time">{{ formatTime(item.sub.create_time) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@oj/api'
import Highlight from '@/pages/oj/components/Highlight'
import time from '@/utils/time'
import { JUDGE_STATUS } from '@/utils/constants'
import { getVoteColor, getVoteFill } from './reviewUtils'

export default {
  name: 'ContestReview',
  components: { Highlight },
  data () {
    return {
      contestID: '',
      activeTeamId: null,
      miniRankRows: [],
      feed: [],
      selectedIndex: -1,
      currentCode: '',
      lastTeamId: null,
      showHidden: false,
      feedUserId: null,
      feedLimit: 50,
      feedTotal: 0,
      feedLoadingMore: false,
      undoStack: [] // {type:'vote', userId, action}
    }
  },
  computed: {
    currentSubmission () { return this.feed[this.selectedIndex] || null },
    currentLanguage () {
      if (!this.currentSubmission) return ''
      const lang = this.currentSubmission.language
      return (lang === 'Python 2' || lang === 'Python 3') ? 'Python' : lang
    },
    visibleRankRows () {
      return this.showHidden ? this.miniRankRows : this.miniRankRows.filter(r => !r.user.hidden)
    },
    hiddenUserIds () {
      return new Set(this.miniRankRows.filter(r => r.user.hidden).map(r => r.user.id))
    },
    displayFeed () {
      return this.feed
        .map((sub, i) => ({ sub, i }))
        .filter(({ sub }) => this.showHidden || this.activeTeamId !== null || !this.hiddenUserIds.has(sub.user_id))
    },
    currentTeamRow () {
      if (!this.currentSubmission) return null
      return this.findRankRow(this.currentSubmission.user_id) || null
    },
    currentTeamHidden () {
      return !!(this.currentTeamRow && this.currentTeamRow.user.hidden)
    }
  },
  mounted () {
    this.contestID = this.$route.params.contestID
    const teamId = this.$route.params.teamId
    this.activeTeamId = teamId ? parseInt(teamId, 10) : null
    this.lastTeamId = this.activeTeamId
    this._onKeydown = this.handleKeydown.bind(this)
    window.addEventListener('keydown', this._onKeydown)
    this.loadRank()
    this.loadFeed(this.activeTeamId)
    this._refreshTimer = setInterval(() => { this.loadRank() }, 10000)
  },
  beforeRouteUpdate (to, from, next) {
    const teamId = to.params.teamId
    this.activeTeamId = teamId ? parseInt(teamId, 10) : null
    this.lastTeamId = this.activeTeamId
    this.loadFeed(this.activeTeamId)
    next()
  },
  beforeDestroy () {
    window.removeEventListener('keydown', this._onKeydown)
    clearInterval(this._refreshTimer)
  },
  methods: {
    getVoteColor,
    getVoteFill,
    loadRank () {
      api.getContestRank({
        offset: 0,
        limit: 200,
        contest_id: this.contestID,
        force_refresh: '1',
        include_review_data: '1'
      })
        .then(res => { this.miniRankRows = res.data.data.results })
    },
    loadFeed (userId = null) {
      this.feedUserId = userId
      const params = { contest_id: this.contestID } // default ordering is -create_time (newest first)
      if (userId) params.user_id = userId
      api.getContestSubmissionList(0, this.feedLimit, params).then(res => {
        this.feed = res.data.data.results
        this.feedTotal = res.data.data.total
        this.selectedIndex = this.feed.length ? 0 : -1
        this.loadCurrentCode()
        this.$nextTick(this.scrollSelectedIntoView)
      })
    },
    loadMoreFeed () {
      if (this.feedLoadingMore || this.feed.length >= this.feedTotal) return Promise.resolve()
      this.feedLoadingMore = true
      const params = { contest_id: this.contestID }
      if (this.feedUserId) params.user_id = this.feedUserId
      return api.getContestSubmissionList(this.feed.length, this.feedLimit, params).then(res => {
        this.feed = this.feed.concat(res.data.data.results)
        this.feedTotal = res.data.data.total
        this.feedLoadingMore = false
      }).catch(() => { this.feedLoadingMore = false })
    },
    onFeedScroll (e) {
      const el = e.target
      if (el.scrollTop + el.clientHeight >= el.scrollHeight - 100) this.loadMoreFeed()
    },
    loadCurrentCode () {
      if (!this.currentSubmission) { this.currentCode = ''; return }
      api.getSubmission(this.currentSubmission.id).then(res => { this.currentCode = res.data.data.code })
    },
    selectTeam (userId) {
      this.lastTeamId = userId
      this.activeTeamId = userId
      this.loadFeed(userId)
    },
    showAllUsers () {
      if (this.activeTeamId === null) {
        // already showing all -- clicking again toggles back to the last-viewed team, if any
        if (this.lastTeamId !== null) this.selectTeam(this.lastTeamId)
        return
      }
      this.lastTeamId = this.activeTeamId
      this.activeTeamId = null
      this.loadFeed(null)
    },
    verdictLabel (result) {
      const status = JUDGE_STATUS[result]
      return status ? (status.short || status.name) : result
    },
    verdictColor (result) {
      const status = JUDGE_STATUS[result]
      return status ? status.highlight : '#515a6e'
    },
    submissionScore (sub) {
      const score = sub.statistic_info && sub.statistic_info.score
      return (score === undefined || score === null) ? '' : `${score}pt`
    },
    formatTime (t) {
      return time.utcToLocal(t)
    },
    selectSubmission (index) {
      this.selectedIndex = index
      this.loadCurrentCode()
      this.$nextTick(this.scrollSelectedIntoView)
    },
    selectNext () {
      const list = this.displayFeed
      const pos = list.findIndex(item => item.i === this.selectedIndex)
      if (pos === -1) { if (list.length) this.selectSubmission(list[0].i); return }
      if (pos < list.length - 1) {
        this.selectSubmission(list[pos + 1].i)
      } else if (this.feed.length < this.feedTotal) {
        // reached the end of what's loaded -- fetch more, then advance once it arrives
        this.loadMoreFeed().then(() => {
          const newList = this.displayFeed
          const newPos = newList.findIndex(item => item.i === this.selectedIndex)
          if (newPos !== -1 && newPos < newList.length - 1) this.selectSubmission(newList[newPos + 1].i)
        })
      }
    },
    selectPrev () {
      const list = this.displayFeed
      const pos = list.findIndex(item => item.i === this.selectedIndex)
      if (pos === -1) { if (list.length) this.selectSubmission(list[0].i); return }
      if (pos > 0) this.selectSubmission(list[pos - 1].i)
    },
    scrollSelectedIntoView () {
      const container = this.$refs.feedContainer
      if (!container) return
      const el = container.querySelector(`[data-feed-index="${this.selectedIndex}"]`)
      if (el) el.scrollIntoView({ block: 'nearest' })
    },
    findRankRow (userId) { return this.miniRankRows.find(r => r.user.id === userId) },
    applyVoteResult (userId, result) {
      const row = this.findRankRow(userId)
      if (row) { row.user.upvotes = result.upvotes; row.user.downvotes = result.downvotes }
    },
    applyHideResult (userId, result) {
      const row = this.findRankRow(userId)
      if (row) { row.user.hidden = result.hidden }
    },
    vote (action) {
      if (!this.currentSubmission) return
      const userId = this.currentSubmission.user_id
      api.teamReviewAction({ contest_id: this.contestID, user_id: userId, action, delta: 1 }).then(res => {
        this.applyVoteResult(userId, res.data.data)
        this.undoStack.push({ type: 'vote', userId, action })
      })
    },
    toggleHide () {
      if (!this.currentSubmission) return
      const userId = this.currentSubmission.user_id
      const row = this.findRankRow(userId)
      const next = row && row.user.hidden ? 'unhide' : 'hide'
      api.teamReviewAction({ contest_id: this.contestID, user_id: userId, action: next }).then(res => {
        this.applyHideResult(userId, res.data.data)
      })
    },
    undo () {
      const last = this.undoStack.pop()
      if (!last) { this.$Message.info('Nothing to undo'); return }
      api.teamReviewAction({ contest_id: this.contestID, user_id: last.userId, action: last.action, delta: -1 })
        .then(res => this.applyVoteResult(last.userId, res.data.data))
    },
    handleKeydown (e) {
      const tag = (e.target.tagName || '').toLowerCase()
      if (tag === 'input' || tag === 'textarea' || e.target.isContentEditable) return
      switch (e.key) {
        case 'j': case 'ArrowDown': e.preventDefault(); this.selectNext(); break
        case 'k': case 'ArrowUp': e.preventDefault(); this.selectPrev(); break
      }
    }
  }
}
</script>

<style scoped lang="less">
.review-container {
  align-items: stretch;
  height: calc(100vh - 160px);
  min-height: 400px;
  overflow: hidden;
  .review-code-pane {
    flex: 1 1 auto;
    min-width: 0;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
  }
  .review-actions {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border-bottom: 1px solid #dcdee2;
    .review-actions-label {
      font-weight: bold;
      margin-right: 4px;
    }
    .review-actions-status {
      font-size: 12px;
      color: #666;
      background: #f0f0f0;
      border-radius: 3px;
      padding: 2px 8px;
      margin-right: 4px;
      white-space: nowrap;
    }
  }
  .review-side-pane {
    flex: 0 0 420px;
    min-height: 0;
    display: flex;
    flex-direction: column;
    .review-mini-rank {
      flex: 2 1 0;
      min-height: 0;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      .review-mini-rank-header {
        flex: 0 0 auto;
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 10px;
        border-bottom: 1px solid #dcdee2;
        .show-hidden-toggle {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          color: #666;
        }
      }
      .review-mini-rank-rows {
        flex: 1 1 auto;
        min-height: 0;
        overflow-y: auto;
      }
    }
    .review-feed {
      flex: 1 1 0;
      min-height: 0;
      overflow-y: auto;
      border-top: 1px solid #dcdee2;
    }
  }
  .review-rank-row, .review-feed-row {
    padding: 6px 10px;
    cursor: pointer;
    display: flex;
    &:hover {
      background: #f8f8f9;
    }
    &.active {
      background: #e8f4ff;
    }
  }
  .review-feed-row {
    justify-content: space-between;
    align-items: center;
  }
  .review-rank-row {
    align-items: stretch;
    &.is-hidden {
      opacity: 0.5;
    }
  }
  .hidden-icon {
    margin-right: 4px;
    color: #ed4014;
  }
  .vote-bar-outer {
    position: relative;
    width: 100%;
    height: 26px;
    border-radius: 3px;
    background: #f0f0f0;
    border: 1px solid #dcdee2;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .vote-bar-inner {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    transition: width 0.2s ease;
  }
  .vote-bar-name {
    position: relative;
    z-index: 1;
    font-size: 12px;
    font-weight: 700;
    line-height: 26px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 0 6px;
    color: #1c2438;
    text-shadow: 0 0 3px rgba(255, 255, 255, 0.85), 0 0 3px rgba(255, 255, 255, 0.85);
  }
  .vote-bar-label {
    position: relative;
    z-index: 1;
    flex: 0 0 auto;
    font-size: 12px;
    font-weight: 600;
    line-height: 26px;
    white-space: nowrap;
    padding: 0 6px;
    color: #1c2438;
    text-shadow: 0 0 3px rgba(255, 255, 255, 0.85), 0 0 3px rgba(255, 255, 255, 0.85);
  }
  .review-feed-row {
    font-size: 12px;
    span {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .feed-username {
      flex: 1 1 30%;
      font-weight: bold;
    }
    .feed-problem {
      flex: 1 1 25%;
    }
    .feed-verdict {
      flex: 0 0 auto;
      font-weight: bold;
      margin: 0 6px;
    }
    .feed-score {
      flex: 0 0 auto;
      color: #2d8cf0;
      margin-right: 6px;
    }
    .feed-time {
      flex: 0 0 auto;
      color: #999;
    }
  }
}
</style>
