<template>
  <div>
    <Panel shadow :padding="10">
      <div slot="title">
        {{title}}
      </div>
      <div slot="extra">
        <Button v-if="listVisible" type="info" @click="init" :loading="btnLoading">{{$t('m.Refresh')}}</Button>
        <Button v-else type="ghost" icon="ios-undo" @click="goBack">{{$t('m.Back')}}</Button>
      </div>

      <div class="no-announcement" v-if="!announcements.length" key="no-announcement">
        <p>{{$t('m.No_Announcements')}}</p>
      </div>
      <div v-if="listVisible">
        <ul class="announcements-container" key="list">
          <li v-for="announcement in announcements" :key="announcement.title">
            <div class="flex-container">
              <div class="title"><a class="entry" @click="goAnnouncement(announcement)">
                {{announcement.title}}</a></div>
              <div class="date">{{announcement.create_time | localtime }}</div>
              <div class="creator"> {{$t('m.By')}} {{announcement.created_by.username}}</div>
            </div>
          </li>
        </ul>
        <Pagination v-if="!isContest"
                    key="page"
                    :total="total"
                    :page-size="limit"
                    @on-change="getAnnouncementList">
        </Pagination>
      </div>

      <div v-else>
        <div v-katex v-html="announcement.content" key="content" class="content-container markdown-body"></div>
      </div>
    </Panel>
  </div>
</template>

<script>
  import api from '@oj/api'
  import {mapGetters, mapActions} from 'vuex'
  import Pagination from '@oj/components/Pagination'

  export default {
    name: 'Announcement',
    components: {
      Pagination
    },
    data () {
      return {
        limit: 10,
        total: 10,
        btnLoading: false,
        generalAnnouncements: [],
        announcement: '',
        listVisible: true,
        contestChecker: null,
        announcementChecker: null
      }
    },
    mounted () {
      this.init()
    },
    beforeDestroy () {
      if (this.contestChecker) {
        clearInterval(this.contestChecker)
      }
      if (this.announcementChecker) {
        clearInterval(this.announcementChecker)
      }
    },
    methods: {
      init () {
        if (this.isContest) {
          this.getContestAnnouncementList()
          this.contestChecker = setInterval(() => { this.getContestAnnouncementList() }, 5000)
        } else {
          this.getAnnouncementList()
          this.announcementChecker = setInterval(() => { this.getAnnouncementList() }, 5000)
        }
      },
      getAnnouncementList (page = 1) {
        this.btnLoading = true
        api.getAnnouncementList((page - 1) * this.limit, this.limit).then(res => {
          this.btnLoading = false
          this.generalAnnouncements = res.data.data.results
          this.total = res.data.data.total
        }, () => {
          this.btnLoading = false
        })
      },
      getContestAnnouncementList () {
        if (this.isContest) {
          this.btnLoading = true
          this.getContestAnnouncements().then(res => {
            this.btnLoading = false
          }, () => {
            this.btnLoading = false
          })
        }
      },
      goAnnouncement (announcement) {
        this.announcement = announcement
        this.listVisible = false
      },
      goBack () {
        this.listVisible = true
        this.announcement = ''
      },
      ...mapActions(['getContestAnnouncements'])
    },
    computed: {
      title () {
        if (this.listVisible) {
          return this.isContest ? this.$i18n.t('m.Contest_Announcements') : this.$i18n.t('m.Announcements')
        } else {
          return this.announcement.title
        }
      },
      isContest () {
        return !!this.$route.params.contestID
      },
      announcements () {
        if (this.isContest) {
          return this.contestAnnouncements
        } else {
          return this.generalAnnouncements
        }
      },
      ...mapGetters(['contestAnnouncements'])
    }
  }
</script>

<style scoped lang="less">
  .announcements-container {
    margin-top: -10px;
    margin-bottom: 10px;
    li {
      padding-top: 15px;
      list-style: none;
      padding-bottom: 15px;
      margin-left: 20px;
      font-size: 16px;
      border-bottom: 1px solid rgba(187, 187, 187, 0.5);
      &:last-child {
        border-bottom: none;
      }
      .flex-container {
        .title {
          flex: 1 1;
          text-align: left;
          padding-left: 10px;
          a.entry {
            color: #495060;
            &:hover {
              color: #2d8cf0;
              border-bottom: 1px solid #2d8cf0;
            }
          }
        }
        .creator {
          flex: none;
          width: 200px;
          text-align: center;
        }
        .date {
          flex: none;
          width: 200px;
          text-align: center;
        }
      }
    }
  }

  .content-container {
    padding: 0 20px 20px 20px;
  }

  .no-announcement {
    text-align: center;
    font-size: 16px;
  }changeLocale

  .announcement-animate-enter-active {
    animation: fadeIn 1s;
  }
</style>
