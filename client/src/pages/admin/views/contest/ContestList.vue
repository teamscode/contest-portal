<template>
  <div class="view">
    <Panel title="Contest List">
      <div slot="header">
        <el-input
          v-model="keyword"
          prefix-icon="el-icon-search"
          placeholder="Keywords"
        />
      </div>
      <el-table
        ref="table"
        v-loading="loading"
        element-loading-text="loading"
        :data="contestList"
        style="width: 100%"
      >
        <el-table-column type="expand">
          <template slot-scope="props">
            <p>Start Time: {{ props.row.start_time | localtime }}</p>
            <p>End Time: {{ props.row.end_time | localtime }}</p>
            <p>Create Time: {{ props.row.create_time | localtime }}</p>
            <p>Creator: {{ props.row.created_by.username }}</p>
          </template>
        </el-table-column>
        <el-table-column
          prop="id"
          width="80"
          label="ID"
        />
        <el-table-column
          prop="title"
          label="Title"
        />
        <el-table-column
          label="Contest Type"
          width="180"
        >
          <template slot-scope="scope">
            <el-tag :type="scope.row.contest_type === 'Public' ? 'success' : 'primary'">
              {{ scope.row.contest_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          label="Status"
          width="130"
        >
          <template slot-scope="scope">
            <el-tag
              :type="scope.row.status === '-1' ? 'danger' : scope.row.status === '0' ? 'success' : 'primary'"
            >
              {{ scope.row.status | contestStatus }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          width="100"
          label="Visible"
        >
          <template slot-scope="scope">
            <el-switch
              v-model="scope.row.visible"
              active-text=""
              inactive-text=""
              @change="handleVisibleSwitch(scope.row)"
            />
          </template>
        </el-table-column>
        <el-table-column
          fixed="right"
          width="250"
        >
          <div slot-scope="scope">
            <icon-btn
              name="Edit"
              icon="edit"
              @click.native="goEdit(scope.row.id)"
            />
            <icon-btn
              name="Problem"
              icon="list-ol"
              @click.native="goContestProblemList(scope.row.id)"
            />
            <icon-btn
              name="Announcement"
              icon="info-circle"
              @click.native="goContestAnnouncement(scope.row.id)"
            />
            <icon-btn
              icon="download"
              name="Download Accepted Submissions"
              @click.native="openDownloadOptions(scope.row.id)"
            />
          </div>
        </el-table-column>
      </el-table>
      <div class="panel-options">
        <el-pagination
          class="page"
          layout="prev, pager, next"
          :page-size="pageSize"
          :total="total"
          @current-change="currentChange"
        />
      </div>
    </Panel>
    <el-dialog
      title="Download Contest Submissions"
      width="30%"
      :visible.sync="downloadDialogVisible"
    >
      <el-switch
        v-model="excludeAdmin"
        active-text="Exclude admin submissions"
      />
      <span
        slot="footer"
        class="dialog-footer"
      >
        <el-button
          type="primary"
          @click="downloadSubmissions"
        >Download</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
  import api from '../../api.js'
  import utils from '@/utils/utils'
  import {CONTEST_STATUS_REVERSE} from '@/utils/constants'

  export default {
    name: 'ContestList',
    filters: {
      contestStatus (value) {
        return CONTEST_STATUS_REVERSE[value].name
      }
    },
    data () {
      return {
        pageSize: 10,
        total: 0,
        contestList: [],
        keyword: '',
        loading: false,
        excludeAdmin: true,
        currentPage: 1,
        currentId: 1,
        downloadDialogVisible: false
      }
    },
    watch: {
      'keyword' () {
        this.currentChange(1)
      }
    },
    mounted () {
      this.getContestList(this.currentPage)
    },
    methods: {
      // 切换页码回调
      currentChange (page) {
        this.currentPage = page
        this.getContestList(page)
      },
      getContestList (page) {
        this.loading = true
        api.getContestList((page - 1) * this.pageSize, this.pageSize, this.keyword).then(res => {
          this.loading = false
          this.total = res.data.data.total
          this.contestList = res.data.data.results
        }, res => {
          this.loading = false
        })
      },
      openDownloadOptions (contestId) {
        this.downloadDialogVisible = true
        this.currentId = contestId
      },
      downloadSubmissions () {
        let excludeAdmin = this.excludeAdmin ? '1' : '0'
        let url = `/admin/download_submissions?contest_id=${this.currentId}&exclude_admin=${excludeAdmin}`
        utils.downloadFile(url)
      },
      goEdit (contestId) {
        this.$router.push({name: 'edit-contest', params: {contestId}})
      },
      goContestAnnouncement (contestId) {
        this.$router.push({name: 'contest-announcement', params: {contestId}})
      },
      goContestProblemList (contestId) {
        this.$router.push({name: 'contest-problem-list', params: {contestId}})
      },
      handleVisibleSwitch (row) {
        api.editContest(row)
      }
    }
  }
</script>
