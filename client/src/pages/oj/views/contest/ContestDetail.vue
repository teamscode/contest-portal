<template>
  <div class="flex-container">
    <div id="contest-main">
      <!--children-->
      <transition name="fadeInUp">
        <router-view />
        <div v-if="route_name === 'contest-details'">
          <Announcements
            :contest-btn-loading="announcementBtnLoading"
            style="margin-bottom: 20px;"
            @refreshAnnouncements="getContestAnnouncementList"
          />
          <div class="flex-container">
            <template>
              <div id="contest-desc">
                <Panel
                  :padding="20"
                  shadow
                >
                  <div slot="title">
                    {{ contest.title }}
                  </div>
                  <div slot="extra">
                    <Tag
                      type="dot"
                      :color="countdownColor"
                    >
                      <span id="countdown">{{ countdown }}</span>
                    </Tag>
                  </div>
                  <div
                    class="markdown-body"
                    v-html="contest.description"
                  />
                  <div
                    v-if="passwordFormVisible"
                    class="contest-password"
                  >
                    <Input
                      v-model="contestPassword"
                      type="password"
                      placeholder="contest password"
                      class="contest-password-input"
                      @on-enter="checkPassword"
                    />
                    <Button
                      type="info"
                      @click="checkPassword"
                    >
                      Enter
                    </Button>
                  </div>
                </Panel>
                <Table
                  :columns="columns"
                  :data="contest_table"
                  disabled-hover
                  style="margin-bottom: 40px;"
                />
              </div>
            </template>
          </div>
        </div>
      </transition>
      <!--children end-->
    </div>
    <div
      v-show="showMenu"
      id="contest-menu"
    >
      <VerticalMenu @on-click="handleRoute">
        <VerticalMenu-item :route="{name: 'contest-details', params: {contestID: contestID}}">
          <Icon type="md-home" />
          {{ $t('m.Home') }}
        </VerticalMenu-item>

        <VerticalMenu-item
          :disabled="contestMenuDisabled"
          :route="{name: 'contest-problem-list', params: {contestID: contestID}}"
        >
          <Icon type="ios-photos" />
          {{ $t('m.Problems') }}
        </VerticalMenu-item>

        <VerticalMenu-item
          v-if="OIContestRealTimePermission"
          :disabled="contestMenuDisabled"
          :route="{name: 'contest-submission-list'}"
        >
          <Icon type="md-list" />
          {{ $t('m.Submissions') }}
        </VerticalMenu-item>

        <VerticalMenu-item
          v-if="OIContestRealTimePermission"
          :disabled="contestMenuDisabled"
          :route="{name: 'contest-rank', params: {contestID: contestID}}"
        >
          <Icon type="ios-stats" />
          {{ $t('m.Rankings') }}
        </VerticalMenu-item>
      </VerticalMenu>
    </div>
  </div>
</template>

<script>
  import moment from 'moment'
  import api from '@oj/api'
  import { mapState, mapGetters, mapActions } from 'vuex'
  import { types } from '@/store'
  import { CONTEST_STATUS_REVERSE, CONTEST_STATUS } from '@/utils/constants'
  import time from '@/utils/time'
  import Announcements from '../general/Announcements.vue'

  export default {
    name: 'ContestDetail',
    components: {Announcements},
    data () {
      return {
        CONTEST_STATUS: CONTEST_STATUS,
        route_name: '',
        announcementBtnLoading: false,
        btnLoading: false,
        contestID: '',
        contestPassword: '',
        contestChecker: null,
        columns: [
          {
            title: this.$i18n.t('m.StartAt'),
            render: (h, params) => {
              return h('span', time.utcToLocal(params.row.start_time))
            }
          },
          {
            title: this.$i18n.t('m.EndAt'),
            render: (h, params) => {
              return h('span', time.utcToLocal(params.row.end_time))
            }
          },
          {
            title: this.$i18n.t('m.ContestType'),
            render: (h, params) => {
              return h('span', params.row.contest_type)
            }
          },
          {
            title: this.$i18n.t('m.Creator'),
            render: (h, data) => {
              return h('span', data.row.created_by.username)
            }
          }
        ],
        lastestAnnouncementTime: 0
      }
    },
    mounted () {
      this.contestID = this.$route.params.contestID
      this.route_name = this.$route.name
      this.$store.dispatch('getContest').then(res => {
        this.changeDomTitle({title: res.data.data.title})
        let data = res.data.data
        let endTime = moment(data.end_time)
        if (endTime.isAfter(moment(data.now))) {
          this.timer = setInterval(() => {
            this.$store.commit(types.NOW_ADD_1S)
          }, 1000)
        }
      })
      this.getContestAnnouncementList()
      this.contestChecker = setInterval(() => { this.getContestAnnouncementList() }, 5000)
    },
    methods: {
      ...mapActions(['changeDomTitle']),
      handleRoute (route) {
        this.$router.push(route)
      },
      checkPassword () {
        if (this.contestPassword === '') {
          this.$error('Password can\'t be empty')
          return
        }
        this.btnLoading = true
        api.checkContestPassword(this.contestID, this.contestPassword).then((res) => {
          this.$success('Succeeded')
          this.$store.commit(types.CONTEST_ACCESS, {access: true})
          this.btnLoading = false
        }, (res) => {
          this.btnLoading = false
        })
      },
      getContestAnnouncementList () {
        this.announcementBtnLoading = true
        this.getContestAnnouncements().then(res => {
          for (let index = 0; index < res.length; index += 1) {
            const announcement = res[index]
            this.$Notice.open({
              title: `Announcement - ${announcement.title}`,
              desc: ` Announcements tab.`,
              render: h => {
                return h('span', [
                  'A new contest announcement has been posted. View in ',
                  h('a', {
                    on: {
                      click: () => {
                        this.$router.push({name: 'contest-details', params: {contestID: this.contestID}})
                      }
                    }
                  }, 'Home Tab.')
                ])
              },
              name: announcement.id,
              duration: 0
            })
          }
          setTimeout(() => { this.announcementBtnLoading = false }, 200)
        }, () => {
          setTimeout(() => { this.announcementBtnLoading = false }, 200)
        })
      },
      ...mapActions(['getContestAnnouncements'])
    },
    computed: {
      ...mapState({
        showMenu: state => state.contest.itemVisible.menu,
        contest: state => state.contest.contest,
        contest_table: state => [state.contest.contest],
        now: state => state.contest.now
      }),
      ...mapGetters(
        ['contestMenuDisabled', 'contestStatus', 'countdown', 'isContestAdmin',
          'OIContestRealTimePermission', 'passwordFormVisible']
      ),
      countdownColor () {
        if (this.contestStatus) {
          return CONTEST_STATUS_REVERSE[this.contestStatus].color
        }
      }
    },
    watch: {
      '$route' (newVal) {
        this.route_name = newVal.name
        this.contestID = newVal.params.contestID
        this.changeDomTitle({title: this.contest.title})
      }
    },
    beforeDestroy () {
      clearInterval(this.timer)
      clearInterval(this.contestChecker)
      this.$Notice.destroy()
      this.$store.commit(types.CLEAR_CONTEST)
    }
  }
</script>

<style scoped lang="less">
  pre {
    display: inline-block;
  }

  #countdown {
    font-size: 16px;
  }

  .flex-container {
    #contest-main {
      flex: 1 1;
      width: 0;
      #contest-desc {
        flex: auto;
      }
    }
    #contest-menu {
      flex: none;
      width: 210px;
      margin-left: 20px;
    }
    .contest-password {
      margin-top: 20px;
      margin-bottom: -10px;
      &-input {
        width: 200px;
        margin-right: 10px;
      }
    }
  }
</style>
