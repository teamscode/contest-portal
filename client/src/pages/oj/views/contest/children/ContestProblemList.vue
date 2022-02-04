<template>
  <div>
    <Panel shadow>
      <div slot="title">
        {{ $t('m.Problems_List') }}
      </div>
      <Table
        v-if="OIContestRealTimePermission"
        context-menu
        show-context-menu
        :columns="ACMTableColumns"
        :data="problems"
        :no-data-text="$t('m.No_Problems')"
        @on-row-click="goContestProblem"
        @on-contextmenu="handleContextMenu"
      >
        <template slot="contextMenu">
            <DropdownItem @click.native="openInNewTab">Open in New Tab</DropdownItem>
        </template>
      </Table>
      <Table
        v-else
        context-menu
        show-context-menu
        :data="problems"
        :columns="OITableColumns"
        no-data-text="$t('m.No_Problems')"
        @on-row-click="goContestProblem"
        @on-contextmenu="handleContextMenu"
      >
        <template slot="contextMenu">
            <DropdownItem @click.native="openInNewTab">Open in New Tab</DropdownItem>
        </template>
      </Table>
    </Panel>
  </div>
</template>

<script>
  import {mapState, mapGetters} from 'vuex'
  import {ProblemMixin} from '@oj/components/mixins'

  export default {
    name: 'ContestProblemList',
    mixins: [ProblemMixin],
    data () {
      return {
        problemId: null,
        ACMTableColumns: [
          {
            title: '#',
            key: '_id',
            width: 150
          },
          {
            title: this.$i18n.t('m.Title'),
            key: 'title'
          },
          {
            title: this.$i18n.t('m.Total'),
            key: 'submission_number'
          },
          {
            title: this.$i18n.t('m.AC_Rate'),
            render: (h, params) => {
              return h('span', this.getACRate(params.row.accepted_number, params.row.submission_number))
            }
          }
        ],
        OITableColumns: [
          {
            title: '#',
            key: '_id',
            width: 150
          },
          {
            title: this.$i18n.t('m.Title'),
            key: 'title'
          }
        ]
      }
    },
    mounted () {
      this.getContestProblems()
    },
    methods: {
      getContestProblems () {
        this.$store.dispatch('getContestProblems').then(res => {
          if (this.isAuthenticated) {
            if (this.OIContestRealTimePermission) {
              this.addStatusColumn(this.ACMTableColumns, res.data.data)
            }
          }
        })
      },
      goContestProblem (row) {
        this.$router.push({
          name: 'contest-problem-details',
          params: {
            contestID: this.$route.params.contestID,
            problemID: row._id
          }
        })
      },
      handleContextMenu (row) {
        this.problemId = row._id
      },
      openInNewTab () {
        window.open(`/contest/${this.$route.params.contestID}/problem/${this.problemId}`, '_blank')
      }
    },
    computed: {
      ...mapState({
        problems: state => state.contest.contestProblems
      }),
      ...mapGetters(['isAuthenticated', 'OIContestRealTimePermission'])
    }
  }
</script>

<style scoped lang="less">
</style>
