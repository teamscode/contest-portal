<template>
  <Row
    type="flex"
    :gutter="18"
  >
    <Col :span="19">
      <Panel shadow>
        <div slot="title">
          {{ $t('m.Problem_List') }}
        </div>
        <div slot="extra">
          <ul class="filter">
            <li>
              <Dropdown @on-click="filterByDifficulty">
                <span>{{ query.difficulty === '' ? $i18n.t('m.Difficulty') : $i18n.t('m.' + query.difficulty) }}
                  <Icon size="20" type="md-arrow-dropdown" />
                </span>
                <Dropdown-menu slot="list">
                  <Dropdown-item name="">
                    {{ $t('m.All') }}
                  </Dropdown-item>
                  <Dropdown-item name="Low">
                    {{ $t('m.Low') }}
                  </Dropdown-item>
                  <Dropdown-item name="Mid">
                    {{ $t('m.Mid') }}
                  </Dropdown-item>
                  <Dropdown-item name="High">
                    {{ $t('m.High') }}
                  </Dropdown-item>
                </Dropdown-menu>
              </Dropdown>
            </li>
            <li>
              <Input
                v-model="query.keyword"
                placeholder="keyword"
                icon="ios-search"
                @on-enter="filterByKeyword"
                @on-click="filterByKeyword"
              />
            </li>
            <li>
              <Button
                type="info"
                @click="onReset"
              >
                <Icon type="md-refresh" />
                {{ $t('m.Reset') }}
              </Button>
            </li>
          </ul>
        </div>
        <Table
          style="width: 100%; font-size: 16px;"
          :columns="problemTableColumns"
          :data="problemList"
          :loading="loadings.table"
          disabled-hover
        />
      </Panel>
      <Pagination
        :total="total"
        :page-size.sync="query.limit"
        :current.sync="query.page"
        :show-sizer="true"
        @on-change="pushRouter"
        @on-page-size-change="pushRouter"
      />
    </Col>

    <Col :span="5">
      <Panel :padding="10">
        <div
          slot="title"
          class="taglist-title"
        >
          {{ $t('m.Tags') }}
        </div>
        <Button
          v-for="tag in tagList"
          :key="tag.name"
          :disabled="query.tag === tag.name"
          shape="circle"
          class="tag-btn"
          @click="filterByTag(tag.name)"
        >
          {{ tag.name }}
        </Button>
      </Panel>
      <Spin
        v-if="loadings.tag"
        fix
        size="large"
      />
    </Col>
  </Row>
</template>

<script>
  import { mapGetters } from 'vuex'
  import api from '@oj/api'
  import utils from '@/utils/utils'
  import { ProblemMixin } from '@oj/components/mixins'
  import Pagination from '@oj/components/Pagination'

  export default {
    name: 'ProblemList',
    components: {
      Pagination
    },
    mixins: [ProblemMixin],
    data () {
      return {
        tagList: [],
        problemTableColumns: [
          {
            title: '#',
            key: '_id',
            width: 80,
            render: (h, params) => {
              return h('Button', {
                props: {
                  type: 'text',
                  size: 'large'
                },
                on: {
                  click: () => {
                    this.$router.push({name: 'problem-details', params: {problemID: params.row._id}})
                  }
                },
                style: {
                  padding: '2px 0'
                }
              }, params.row._id)
            }
          },
          {
            title: this.$i18n.t('m.Title'),
            width: 400,
            render: (h, params) => {
              return h('Button', {
                props: {
                  type: 'text',
                  size: 'large'
                },
                on: {
                  click: () => {
                    this.$router.push({name: 'problem-details', params: {problemID: params.row._id}})
                  }
                },
                style: {
                  padding: '2px 0',
                  overflowX: 'auto',
                  textAlign: 'left',
                  width: '100%'
                }
              }, params.row.title)
            }
          },
          {
            title: this.$i18n.t('m.Level'),
            render: (h, params) => {
              let t = params.row.difficulty
              let color = 'blue'
              if (t === 'Low') color = 'green'
              else if (t === 'High') color = 'yellow'
              return h('Tag', {
                props: {
                  color: color
                }
              }, this.$i18n.t('m.' + params.row.difficulty))
            }
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
          },
          {
            title: this.$i18n.t('m.Tags'),
            align: 'center',
            render: (h, params) => {
              let tags = []
              params.row.tags.forEach(tag => {
                tags.push(h('Tag', {}, tag))
              })
              return h('div', {
                style: {
                  margin: '8px 0'
                }
              }, tags)
            }
          }
        ],
        problemList: [],
        limit: 20,
        total: 0,
        loadings: {
          table: true,
          tag: true
        },
        routeName: '',
        query: {
          keyword: '',
          difficulty: '',
          tag: '',
          page: 1,
          limit: 10
        }
      }
    },
    mounted () {
      this.init()
    },
    methods: {
      init (simulate = false) {
        this.routeName = this.$route.name
        let query = this.$route.query
        this.query.difficulty = query.difficulty || ''
        this.query.keyword = query.keyword || ''
        this.query.tag = query.tag || ''
        this.query.page = parseInt(query.page) || 1
        if (this.query.page < 1) {
          this.query.page = 1
        }
        this.query.limit = parseInt(query.limit) || 10
        if (!simulate) {
          this.getTagList()
        }
        this.getProblemList()
      },
      pushRouter () {
        this.$router.push({
          name: 'problem-list',
          query: utils.filterEmptyValue(this.query)
        })
      },
      getProblemList () {
        let offset = (this.query.page - 1) * this.query.limit
        this.loadings.table = true
        api.getProblemList(offset, this.limit, this.query).then(res => {
          this.loadings.table = false
          this.total = res.data.data.total
          this.problemList = res.data.data.results
          if (this.isAuthenticated) {
            this.addStatusColumn(this.problemTableColumns, res.data.data.results)
          }
        }, res => {
          this.loadings.table = false
        })
      },
      getTagList () {
        api.getProblemTagList().then(res => {
          this.tagList = res.data.data
          this.loadings.tag = false
        }, res => {
          this.loadings.tag = false
        })
      },
      filterByTag (tagName) {
        this.query.tag = tagName
        this.query.page = 1
        this.pushRouter()
      },
      filterByDifficulty (difficulty) {
        this.query.difficulty = difficulty
        this.query.page = 1
        this.pushRouter()
      },
      filterByKeyword () {
        this.query.page = 1
        this.pushRouter()
      },
      onReset () {
        this.$router.push({name: 'problem-list'})
      }
    },
    computed: {
      ...mapGetters(['isAuthenticated'])
    },
    watch: {
      '$route' (newVal, oldVal) {
        if (newVal !== oldVal) {
          this.init(true)
        }
      },
      'isAuthenticated' (newVal) {
        if (newVal === true) {
          this.init()
        }
      }
    }
  }
</script>

<style scoped lang="less">
  .taglist-title {
    margin-left: -10px;
    margin-bottom: -10px;
  }

  .tag-btn {
    margin-right: 5px;
    margin-bottom: 10px;
  }

  #pick-one {
    margin-top: 10px;
  }
</style>
