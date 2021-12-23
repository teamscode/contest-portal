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

      <div class="no-announcement" v-if="!announcements.length" key="no-announcement" style="margin-bottom: 20px; margin-top: 10px;">
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
        <Button v-else type="ghost" @click="$Notice.destroy" style="margin-left: 10px;">Dismiss All Notifications</Button>
      </div>

      <div v-else>
        <div v-katex v-html="announcement.content" key="content" class="content-container markdown-body"></div>
      </div>
    </Panel>
  </div>
</template>

<script>
  import api from '@oj/api'
  import {mapGetters} from 'vuex'
  import Pagination from '@oj/components/Pagination'

  export default {
    name: 'Announcement',
    components: {
      Pagination
    },
    props: ['contestBtnLoading'],
    data () {
      return {
        limit: 10,
        total: 10,
        generalBtnLoading: false,
        generalAnnouncements: [],
        announcement: '',
        listVisible: true,
        announcementChecker: null
      }
    },
    mounted () {
      this.init()
      this.announcementChecker = setInterval(() => { this.getAnnouncementList() }, 5000)
    },
    beforeDestroy () {
      if (this.announcementChecker) {
        clearInterval(this.announcementChecker)
      }
    },
    methods: {
      init () {
        if (this.isContest) {
          this.$emit('refreshAnnouncements')
        } else {
          this.getAnnouncementList()
        }
      },
      getAnnouncementList (page = 1) {
        this.generalBtnLoading = true
        api.getAnnouncementList((page - 1) * this.limit, this.limit).then(res => {
          setTimeout(() => { this.generalBtnLoading = false }, 200)
          this.generalAnnouncements = res.data.data.results
          this.total = res.data.data.total
        }, () => {
          setTimeout(() => { this.generalBtnLoading = false }, 200)
        })
      },
      goAnnouncement (announcement) {
        this.announcement = announcement
        this.$Notice.close(announcement.id)
        this.listVisible = false
      },
      goBack () {
        this.listVisible = true
        this.announcement = ''
      }
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
      btnLoading () {
        if (this.isContest) {
          return this.contestBtnLoading
        } else {
          return this.generalBtnLoading
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
