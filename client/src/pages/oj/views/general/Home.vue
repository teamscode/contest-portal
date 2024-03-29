<template>
  <Row
    type="flex"
    justify="space-around"
  >
    <Col :span="24">
      <panel
        v-if="contests.length"
        shadow
        class="contest"
      >
        <div slot="title">
          <Button
            type="text"
            class="contest-title"
            @click="goContest"
          >
            {{ contests[index].title }}
          </Button>
        </div>
        <Carousel
          v-model="index"
          trigger="hover"
          autoplay
          :autoplay-speed="6000"
          class="contest"
        >
          <CarouselItem
            v-for="(contest, index) of contests"
            :key="index"
          >
            <div class="contest-content">
              <div class="contest-content-tags">
                <Button
                  type="info"
                  shape="circle"
                  size="small"
                  icon="ios-calendar"
                >
                  {{ contest.start_time | localtime('YYYY-M-D HH:mm') }}
                </Button>
                <Button
                  type="success"
                  shape="circle"
                  size="small"
                  icon="md-time"
                >
                  {{ getDuration(contest.start_time, contest.end_time) }}
                </Button>
              </div>
              <div class="contest-content-description">
                <blockquote v-html="contest.description" />
              </div>
            </div>
          </CarouselItem>
        </Carousel>
      </panel>
      <Announcements />
    </Col>
  </Row>
</template>

<script>
  import Announcements from './Announcements.vue'
  import api from '@oj/api'
  import time from '@/utils/time'
  import { CONTEST_STATUS } from '@/utils/constants'
  import { mapGetters } from 'vuex'

  export default {
    name: 'Home',
    components: {
      Announcements
    },
    data () {
      return {
        contests: [],
        index: 0
      }
    },
    methods: {
      getDuration (startTime, endTime) {
        return time.duration(startTime, endTime)
      },
      goContest () {
        this.$router.push({
          name: 'contest-details',
          params: {contestID: this.contests[this.index].id}
        })
      }
    },
    mounted () {
      if (this.isAuthenticated) {
        let params = {status: CONTEST_STATUS.NOT_START}
        api.getContestList(0, 5, params).then(res => {
          this.contests = res.data.data.results
        })
      }
    },
    computed: {
      ...mapGetters(['isAuthenticated'])
    },
    watch: {
      'isAuthenticated' () {
        if (this.isAuthenticated) {
          let params = {status: CONTEST_STATUS.NOT_START}
          api.getContestList(0, 5, params).then(res => {
            this.contests = res.data.data.results
          })
        }
      }
    }
  }
</script>

<style lang="less" scoped>
  .contest {
    &-title {
      font-style: italic;
      font-size: 21px;
    }
    &-content {
      padding: 0 70px 40px 70px;
      &-description {
        margin-top: 25px;
      }
    }
    margin-bottom: 20px;
  }
</style>
