<template>
  <div class="view">
    <Panel :title="contestId ? $i18n.t('m.Contest_Problem_List') : $i18n.t('m.Problem_List')">
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
        :data="problemList"
        style="width: 100%"
        @row-dblclick="handleDblclick"
      >
        <el-table-column
          width="100"
          prop="id"
          label="ID"
        />
        <el-table-column
          width="150"
          label="Display ID"
        >
          <template slot-scope="{row}">
            <span v-show="!row.isEditing">{{ row._id }}</span>
            <el-input
              v-show="row.isEditing"
              v-model="row._id"
              @keyup.enter.native="handleInlineEdit(row)"
            />
          </template>
        </el-table-column>
        <el-table-column
          prop="title"
          label="Title"
        >
          <template slot-scope="{row}">
            <span v-show="!row.isEditing">{{ row.title }}</span>
            <el-input
              v-show="row.isEditing"
              v-model="row.title"
              @keyup.enter.native="handleInlineEdit(row)"
            />
          </template>
        </el-table-column>
        <el-table-column
          prop="created_by.username"
          label="Author"
        />
        <el-table-column
          width="200"
          prop="create_time"
          label="Create Time"
        >
          <template slot-scope="scope">
            {{ scope.row.create_time | localtime }}
          </template>
        </el-table-column>
        <el-table-column
          v-if="contestId"
          width="100"
          prop="visible"
          label="Visible"
        >
          <template slot-scope="scope">
            <el-switch
              v-model="scope.row.visible"
              active-text=""
              inactive-text=""
              @change="updateProblem(scope.row)"
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
              icon="download"
              name="Download Test Cases"
              @click.native="downloadTestCase(scope.row.id)"
            />
            <icon-btn
              icon="trash"
              name="Delete Problem"
              @click.native="deleteProblem(scope.row.id)"
            />
          </div>
        </el-table-column>
      </el-table>
      <div class="panel-options">
        <el-button
          type="primary"
          size="small"
          icon="el-icon-plus"
          @click="goCreateProblem"
        >
          Create
        </el-button>
        <el-button
          v-if="contestId"
          type="primary"
          size="small"
          icon="el-icon-plus"
          @click="addProblemDialogVisible = true"
        >
          Add From Problem Bank
        </el-button>
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
      title="Sure to update the problem? "
      width="20%"
      :visible.sync="InlineEditDialogVisible"
      @close-on-click-modal="false"
    >
      <div>
        <p>DisplayID: {{ currentRow._id }}</p>
        <p>Title: {{ currentRow.title }}</p>
      </div>
      <span slot="footer">
        <cancel @click.native="InlineEditDialogVisible = false; getProblemList(currentPage)" />
        <save @click.native="updateProblem(currentRow)" />
      </span>
    </el-dialog>
    <el-dialog
      v-if="contestId"
      title="Add Contest Problem"
      width="80%"
      :visible.sync="addProblemDialogVisible"
      @close-on-click-modal="false"
    >
      <add-problem-component
        :contest-i-d="contestId"
        @on-change="getProblemList"
      />
    </el-dialog>
  </div>
</template>

<script>
  import api from '../../api.js'
  import utils from '@/utils/utils'
  import AddProblemComponent from './AddPublicProblem.vue'

  export default {
    name: 'ProblemList',
    components: {
      AddProblemComponent
    },
    data () {
      return {
        pageSize: 10,
        total: 0,
        problemList: [],
        keyword: '',
        loading: false,
        currentPage: 1,
        routeName: '',
        contestId: '',
        // for make public use
        currentProblemID: '',
        currentRow: {},
        InlineEditDialogVisible: false,
        makePublicDialogVisible: false,
        addProblemDialogVisible: false
      }
    },
    watch: {
      '$route' (newVal, oldVal) {
        this.contestId = newVal.params.contestId
        this.routeName = newVal.name
        this.getProblemList(this.currentPage)
      },
      'keyword' () {
        this.currentChange()
      }
    },
    mounted () {
      this.routeName = this.$route.name
      this.contestId = this.$route.params.contestId
      this.getProblemList(this.currentPage)
    },
    methods: {
      handleDblclick (row) {
        row.isEditing = true
      },
      goEdit (problemId) {
        if (this.routeName === 'problem-list') {
          this.$router.push({name: 'edit-problem', params: {problemId}})
        } else if (this.routeName === 'contest-problem-list') {
          this.$router.push({name: 'edit-contest-problem', params: {problemId: problemId, contestId: this.contestId}})
        }
      },
      goCreateProblem () {
        if (this.routeName === 'problem-list') {
          this.$router.push({name: 'create-problem'})
        } else if (this.routeName === 'contest-problem-list') {
          this.$router.push({name: 'create-contest-problem', params: {contestId: this.contestId}})
        }
      },
      // 切换页码回调
      currentChange (page) {
        this.currentPage = page
        this.getProblemList(page)
      },
      getProblemList (page = 1) {
        this.loading = true
        let funcName = this.routeName === 'problem-list' ? 'getProblemList' : 'getContestProblemList'
        let params = {
          limit: this.pageSize,
          offset: (page - 1) * this.pageSize,
          keyword: this.keyword,
          contest_id: this.contestId
        }
        api[funcName](params).then(res => {
          this.loading = false
          this.total = res.data.data.total
          for (let problem of res.data.data.results) {
            problem.isEditing = false
          }
          this.problemList = res.data.data.results
        }, res => {
          this.loading = false
        })
      },
      deleteProblem (id) {
        this.$confirm('Sure to delete this problem? The associated submissions will be deleted as well.', 'Delete Problem', {
          type: 'warning'
        }).then(() => {
          let funcName = this.routeName === 'problem-list' ? 'deleteProblem' : 'deleteContestProblem'
          api[funcName](id).then(() => [
            this.getProblemList(this.currentPage - 1)
          ]).catch(() => {
          })
        }, () => {
        })
      },
      updateProblem (row) {
        let data = Object.assign({}, row)
        let funcName = ''
        if (this.contestId) {
          data.contest_id = this.contestId
          funcName = 'editContestProblem'
        } else {
          funcName = 'editProblem'
        }
        api[funcName](data).then(res => {
          this.InlineEditDialogVisible = false
          this.getProblemList(this.currentPage)
        }).catch(() => {
          this.InlineEditDialogVisible = false
        })
      },
      handleInlineEdit (row) {
        this.currentRow = row
        this.InlineEditDialogVisible = true
      },
      downloadTestCase (problemID) {
        let url = '/admin/test_case?problem_id=' + problemID
        utils.downloadFile(url)
      },
      getPublicProblem () {
        api.getProblemList()
      }
    }
  }
</script>

<style scoped lang="less">
</style>
