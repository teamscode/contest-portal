<template>
  <div>
    <el-input
      v-model="keyword"
      placeholder="Keywords"
      prefix-icon="el-icon-search"
    />
    <el-table
      v-loading="loading"
      :data="problems"
    >
      <el-table-column
        label="ID"
        width="100"
        prop="id"
      />
      <el-table-column
        label="DisplayID"
        width="200"
        prop="_id"
      />
      <el-table-column
        label="Title"
        prop="title"
      />
      <el-table-column
        align="center"
        width="100"
        fixed="right"
      >
        <template slot-scope="{row}">
          <icon-btn
            icon="plus"
            name="Add the problem"
            @click.native="handleAddProblem(row.id)"
          />
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      class="page"
      layout="prev, pager, next"
      :page-size="limit"
      :total="total"
      @current-change="getPublicProblem"
    />
  </div>
</template>
<script>
  import api from '@admin/api'

  export default {
    name: 'AddProblemFromPublic',
    props: ['contestID'],
    data () {
      return {
        page: 1,
        limit: 10,
        total: 0,
        loading: false,
        problems: [],
        contest: {},
        keyword: ''
      }
    },
    watch: {
      'keyword' () {
        this.getPublicProblem(this.page)
      }
    },
    mounted () {
      api.getContest(this.contestID).then(res => {
        this.contest = res.data.data
        this.getPublicProblem()
      }).catch(() => {
      })
    },
    methods: {
      getPublicProblem (page) {
        this.loading = true
        let params = {
          keyword: this.keyword,
          offset: (page - 1) * this.limit,
          limit: this.limit
        }
        api.getProblemList(params).then(res => {
          this.loading = false
          this.total = res.data.data.total
          this.problems = res.data.data.results
        }).catch(() => {
        })
      },
      handleAddProblem (problemID) {
        this.$prompt('Please input display id for the contest problem', 'confirm').then(({value}) => {
          let data = {
            problem_id: problemID,
            contest_id: this.contestID,
            display_id: value
          }
          api.addProblemFromPublic(data).then(() => {
            this.$emit('on-change')
          }, () => {
          })
        }, () => {
        })
      }
    }
  }
</script>
<style scoped>
  .page {
    margin-top: 20px;
    text-align: right
  }

</style>
