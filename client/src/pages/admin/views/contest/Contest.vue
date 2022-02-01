<template>
  <div class="view">
    <Panel :title="title">
      <el-form label-position="top">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item
              :label="$t('m.ContestTitle')"
              required
            >
              <el-input
                v-model="contest.title"
                :placeholder="$t('m.ContestTitle')"
              />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item
              :label="$t('m.ContestDescription')"
              required
            >
              <Simditor v-model="contest.description" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item
              :label="$t('m.Contest_Start_Time')"
              required
            >
              <el-date-picker
                v-model="contest.start_time"
                type="datetime"
                :placeholder="$t('m.Contest_Start_Time')"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item
              :label="$t('m.Contest_End_Time')"
              required
            >
              <el-date-picker
                v-model="contest.end_time"
                type="datetime"
                :placeholder="$t('m.Contest_End_Time')"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('m.Contest_Password')">
              <el-input
                v-model="contest.password"
                :placeholder="$t('m.Contest_Password')"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('m.Real_Time_Rank')">
              <el-switch
                v-model="contest.real_time_rank"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('m.Contest_Status')">
              <el-switch
                v-model="contest.visible"
                active-text=""
                inactive-text=""
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Division" required>
              <el-select
                v-model="contest.division"
                placeholder="Division"
              >
                <el-option
                  label="Advanced"
                  value="Advanced"
                />
                <el-option
                  label="Intermediate"
                  value="Intermediate"
                />
                <el-option
                  label="Novice"
                  value="Novice"
                />
                <el-option
                  label="Testing"
                  value="Testing"
                />
                <el-option
                  label="All"
                  value="All"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item :label="$t('m.Allowed_IP_Ranges')">
              <div
                v-for="(range, index) in contest.allowed_ip_ranges"
                :key="index"
              >
                <el-row
                  :gutter="20"
                  style="margin-bottom: 15px"
                >
                  <el-col :span="8">
                    <el-input
                      v-model="range.value"
                      :placeholder="$t('m.CIDR_Network')"
                    />
                  </el-col>
                  <el-col :span="10">
                    <el-button
                      plain
                      icon="el-icon-fa-plus"
                      @click="addIPRange"
                    />
                    <el-button
                      plain
                      icon="el-icon-fa-trash"
                      @click="removeIPRange(range)"
                    />
                  </el-col>
                </el-row>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <save @click.native="saveContest" />
    </Panel>
  </div>
</template>

<script>
  import api from '../../api.js'
  import Simditor from '../../components/Simditor.vue'

  export default {
    name: 'CreateContest',
    components: {
      Simditor
    },
    data () {
      return {
        title: 'Create Contest',
        disableRuleType: false,
        contest: {
          title: '',
          description: '',
          start_time: '',
          end_time: '',
          password: '',
          real_time_rank: true,
          visible: true,
          allowed_ip_ranges: [{
            value: ''
          }]
        }
      }
    },
    mounted () {
      if (this.$route.name === 'edit-contest') {
        this.title = 'Edit Contest'
        this.disableRuleType = true
        api.getContest(this.$route.params.contestId).then(res => {
          let data = res.data.data
          let ranges = []
          for (let v of data.allowed_ip_ranges) {
            ranges.push({value: v})
          }
          if (ranges.length === 0) {
            ranges.push({value: ''})
          }
          data.allowed_ip_ranges = ranges
          this.contest = data
        }).catch(() => {
        })
      }
    },
    methods: {
      saveContest () {
        let funcName = this.$route.name === 'edit-contest' ? 'editContest' : 'createContest'
        let data = Object.assign({}, this.contest)
        let ranges = []
        for (let v of data.allowed_ip_ranges) {
          if (v.value !== '') {
            ranges.push(v.value)
          }
        }
        data.allowed_ip_ranges = ranges
        api[funcName](data).then(res => {
          this.$router.push({name: 'contest-list', query: {refresh: 'true'}})
        }).catch(() => {
        })
      },
      addIPRange () {
        this.contest.allowed_ip_ranges.push({value: ''})
      },
      removeIPRange (range) {
        let index = this.contest.allowed_ip_ranges.indexOf(range)
        if (index !== -1) {
          this.contest.allowed_ip_ranges.splice(index, 1)
        }
      }
    }
  }
</script>
