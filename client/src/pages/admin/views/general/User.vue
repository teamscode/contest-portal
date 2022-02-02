<template>
  <div class="view">
    <Panel :title="$t('m.User_User') ">
      <div slot="header">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-button
              v-show="selectedUsers.length"
              type="warning"
              icon="el-icon-fa-trash"
              @click="deleteUsers(selectedUserIDs)"
            >
              Delete
            </el-button>
          </el-col>
          <el-col :span="selectedUsers.length ? 16: 24">
            <el-input
              v-model="keyword"
              prefix-icon="el-icon-search"
              placeholder="Keywords"
            />
          </el-col>
        </el-row>
      </div>
      <el-table
        ref="table"
        v-loading="loadingTable"
        element-loading-text="loading"
        :data="userList"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column
          type="selection"
          width="55"
        />

        <el-table-column
          prop="id"
          label="ID"
        />

        <el-table-column
          prop="username"
          label="Username"
        />

        <el-table-column
          prop="create_time"
          label="Create Time"
        >
          <template slot-scope="scope">
            {{ scope.row.create_time | localtime }}
          </template>
        </el-table-column>

        <el-table-column
          prop="last_login"
          label="Last Login"
        >
          <template slot-scope="scope">
            {{ scope.row.last_login | localtime }}
          </template>
        </el-table-column>

        <el-table-column
          prop="team_members"
          label="Team Members"
        >
          <template slot-scope="scope">
            {{ scope.row.team_members.map(member=>member.name).join(", ") }}
          </template>
        </el-table-column>

        <el-table-column
          prop="email"
          label="Email"
        />

        <el-table-column
          prop="admin_type"
          label="User Role"
        >
          <template slot-scope="scope">
            {{ scope.row.admin_type }}
          </template>
        </el-table-column>

        <el-table-column
          fixed="right"
          width="200"
        >
          <template slot-scope="{row}">
            <icon-btn
              name="Edit"
              icon="edit"
              @click.native="openUserDialog(row.id)"
            />
            <icon-btn
              name="Delete"
              icon="trash"
              @click.native="deleteUsers([row.id])"
            />
          </template>
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

    <Panel>
      <span slot="title">{{ $t('m.Import_User') }}
      </span>
      <el-upload
        v-if="!uploadUsers.length"
        action=""
        :show-file-list="false"
        accept=".csv"
        :before-upload="handleUsersCSV"
      >
        <el-button
          size="small"
          icon="el-icon-fa-upload"
          type="primary"
        >
          Choose File
        </el-button>
      </el-upload>
      <template v-else>
        <el-table :data="uploadUsersPage">
          <el-table-column label="Username">
            <template slot-scope="{row}">
              {{ row[0] }}
            </template>
          </el-table-column>
          <el-table-column label="Password">
            <template slot-scope="{row}">
              {{ row[1] }}
            </template>
          </el-table-column>
          <el-table-column label="Email">
            <template slot-scope="{row}">
              {{ row[2] }}
            </template>
          </el-table-column>
          <el-table-column label="Team Members">
            <template slot-scope="{row}">
              {{ row[3] }}
            </template>
          </el-table-column>
        </el-table>
        <div class="panel-options">
          <el-button
            type="primary"
            size="small"
            icon="el-icon-fa-upload"
            @click="handleUsersUpload"
          >
            Import All
          </el-button>
          <el-button
            type="warning"
            size="small"
            icon="el-icon-fa-undo"
            @click="handleResetData"
          >
            Reset Data
          </el-button>
          <el-pagination
            class="page"
            layout="prev, pager, next"
            :page-size="uploadUsersPageSize"
            :current-page.sync="uploadUsersCurrentPage"
            :total="uploadUsers.length"
          />
        </div>
      </template>
    </Panel>

    <Panel :title="$t('m.Generate_User')">
      <el-form
        ref="formGenerateUser"
        :model="formGenerateUser"
      >
        <el-row
          type="flex"
          justify="space-between"
        >
          <el-col :span="4">
            <el-form-item
              label="Prefix"
              prop="prefix"
            >
              <el-input
                v-model="formGenerateUser.prefix"
                placeholder="Prefix"
              />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item
              label="Suffix"
              prop="suffix"
            >
              <el-input
                v-model="formGenerateUser.suffix"
                placeholder="Suffix"
              />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item
              label="Start Number"
              prop="number_from"
              required
            >
              <el-input-number
                v-model="formGenerateUser.number_from"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item
              label="End Number"
              prop="number_to"
              required
            >
              <el-input-number
                v-model="formGenerateUser.number_to"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item
              label="Password Length"
              prop="password_length"
              required
            >
              <el-input
                v-model="formGenerateUser.password_length"
                placeholder="Password Length"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button
            type="primary"
            icon="el-icon-fa-users"
            :loading="loadingGenerate"
            @click="generateUser"
          >
            Generate & Export
          </el-button>
          <span
            v-if="formGenerateUser.number_from && formGenerateUser.number_to &&
              formGenerateUser.number_from <= formGenerateUser.number_to"
            class="userPreview"
          >
            The usernames will be {{ formGenerateUser.prefix + formGenerateUser.number_from + formGenerateUser.suffix }},
            <span v-if="formGenerateUser.number_from + 1 < formGenerateUser.number_to">
              {{ formGenerateUser.prefix + (formGenerateUser.number_from + 1) + formGenerateUser.suffix + '...' }}
            </span>
            <span v-if="formGenerateUser.number_from + 1 <= formGenerateUser.number_to">
              {{ formGenerateUser.prefix + formGenerateUser.number_to + formGenerateUser.suffix }}
            </span>
          </span>
        </el-form-item>
      </el-form>
    </Panel>
    <!--对话框-->
    <el-dialog
      :title="$t('m.User_Info')"
      :visible.sync="showUserDialog"
      :close-on-click-modal="false"
      width="900px"
    >
      <el-form
        :model="user"
        label-width="160px"
        label-position="left"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item
              :label="$t('m.User_Username')"
              required
            >
              <el-input v-model="user.username" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item
              label="Team Size"
              required
            >
              <el-input-number v-model="user.membersCount" @change="changeMembersCount" :min="1" :max="4"></el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item
              label="Team Name"
              required
            >
              <el-input v-model="user.team_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item
              v-for="(member, index) in user.team_members"
              :key="index"
              :label="'Member #'+(index+1)"
              required
            >
              <el-input placeholder="Name" v-model="member.name" />
              <el-input placeholder="Class" style="margin-top: 10px" v-model.number="member.year" />
              <el-input placeholder="Email" style="margin-top: 10px" v-model="member.email" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item
              :label="$t('m.User_Email')"
              required
            >
              <el-input v-model="user.email" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('m.User_New_Password')">
              <el-input v-model="user.password" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('m.User_Type')">
              <el-select v-model="user.admin_type">
                <el-option
                  label="Regular User"
                  value="Regular User"
                />
                <el-option
                  label="Admin"
                  value="Admin"
                />
                <el-option
                  label="Super Admin"
                  value="Super Admin"
                />
                <el-option
                  label="Tester"
                  value="Tester"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Division">
              <el-select v-model="user.division">
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
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('m.Problem_Permission')">
              <el-select
                v-model="user.problem_permission"
                :disabled="user.admin_type!=='Admin'"
              >
                <el-option
                  label="None"
                  value="None"
                />
                <el-option
                  label="Own"
                  value="Own"
                />
                <el-option
                  label="All"
                  value="All"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('m.Two_Factor_Auth')">
              <el-switch
                v-model="user.two_factor_auth"
                :disabled="!user.real_tfa"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Open API">
              <el-switch
                v-model="user.open_api"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Disabled">
              <el-switch
                v-model="user.is_disabled"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <span
        slot="footer"
        class="dialog-footer"
      >
        <cancel @click.native="showUserDialog = false">Cancel</cancel>
        <save @click.native="saveUser()" />
      </span>
    </el-dialog>
  </div>
</template>

<script>
  import papa from 'papaparse'
  import api from '../../api.js'
  import utils from '@/utils/utils'

  export default {
    name: 'User',
    data () {
      return {
        // 一页显示的用户数
        pageSize: 10,
        // 用户总数
        total: 0,
        // 用户列表
        userList: [],
        uploadUsers: [],
        uploadUsersPage: [],
        uploadUsersCurrentPage: 1,
        uploadUsersPageSize: 15,
        // 搜索关键字
        keyword: '',
        // 是否显示用户对话框
        showUserDialog: false,
        // 当前用户model
        user: {},
        loadingTable: false,
        loadingGenerate: false,
        // 当前页码
        currentPage: 0,
        selectedUsers: [],
        formGenerateUser: {
          prefix: '',
          suffix: '',
          number_from: 0,
          number_to: 0,
          password_length: 8
        }
      }
    },
    computed: {
      selectedUserIDs () {
        let ids = []
        for (let user of this.selectedUsers) {
          ids.push(user.id)
        }
        return ids
      }
    },
    watch: {
      'keyword' () {
        this.currentChange(1)
      },
      'user.admin_type' () {
        if (this.user.admin_type === 'Super Admin') {
          this.user.problem_permission = 'All'
        } else if (this.user.admin_type === 'Regular User' || this.user.admin_type === 'Tester') {
          this.user.problem_permission = 'None'
        }
      },
      'uploadUsersCurrentPage' (page) {
        this.uploadUsersPage = this.uploadUsers.slice((page - 1) * this.uploadUsersPageSize, page * this.uploadUsersPageSize)
      }
    },
    mounted () {
      this.getUserList(1)
    },
    methods: {
      // 切换页码回调
      currentChange (page) {
        this.currentPage = page
        this.getUserList(page)
      },
      // 提交修改用户的信息
      saveUser () {
        api.editUser(this.user).then(res => {
          // 更新列表
          this.getUserList(this.currentPage)
        }).then(() => {
          this.showUserDialog = false
        }).catch(() => {
        })
      },
      // 打开用户对话框
      openUserDialog (id) {
        this.showUserDialog = true
        api.getUser(id).then(res => {
          const userData = res.data.data
          userData.password = ''
          this.user = userData
          this.user.membersCount = this.user.team_members.length
          this.user.real_tfa = this.user.two_factor_auth
        })
      },
      changeMembersCount () {
        this.user.team_members.splice(this.user.membersCount)
        while (
          this.user.team_members.length < this.user.membersCount
        ) {
          this.user.team_members.push({ name: '', email: '' })
        }
      },
      // 获取用户列表
      getUserList (page) {
        this.loadingTable = true
        api.getUserList((page - 1) * this.pageSize, this.pageSize, this.keyword).then(res => {
          this.loadingTable = false
          this.total = res.data.data.total
          this.userList = res.data.data.results
          console.log(this.userList)
        }, res => {
          this.loadingTable = false
        })
      },
      deleteUsers (ids) {
        this.$confirm('Sure to delete the user? The associated resources created by this user will be deleted as well, like problem, contest, announcement, etc.', 'confirm', {
          type: 'warning'
        }).then(() => {
          api.deleteUsers(ids.join(',')).then(res => {
            this.getUserList(this.currentPage)
          }).catch(() => {
            this.getUserList(this.currentPage)
          })
        }, () => {
        })
      },
      handleSelectionChange (val) {
        this.selectedUsers = val
      },
      generateUser () {
        this.$refs['formGenerateUser'].validate((valid) => {
          if (!valid) {
            this.$error('Please validate the error fields')
            return
          }
          this.loadingGenerate = true
          let data = Object.assign({}, this.formGenerateUser)
          api.generateUser(data).then(res => {
            this.loadingGenerate = false
            let url = '/admin/generate_user?file_id=' + res.data.data.file_id
            utils.downloadFile(url).then(() => {
              this.$alert('All users created successfully, the users sheets have downloaded to your disk.', 'Notice')
            })
            this.getUserList(1)
          }).catch(() => {
            this.loadingGenerate = false
          })
        })
      },
      handleUsersCSV (file) {
        papa.parse(file, {
          complete: (results) => {
            let data = results.data.filter(user => {
              return user[0] && user[1] && user[2] && user[3]
            })
            console.log(data)
            console.log(results.data)
            let delta = results.data.length - data.length - 1
            if (delta > 0) {
              this.$warning(delta + ' users have been filtered due to empty value')
            }
            this.uploadUsersCurrentPage = 1
            this.uploadUsers = data
            this.uploadUsersPage = data.slice(0, this.uploadUsersPageSize)
          },
          error: (error) => {
            this.$error(error)
          }
        })
      },
      handleUsersUpload () {
        api.importUsers(this.uploadUsers).then(res => {
          this.getUserList(1)
          this.handleResetData()
        }).catch(() => {
        })
      },
      handleResetData () {
        this.uploadUsers = []
      }
    }
  }
</script>

<style scoped lang="less">
  .import-user-icon {
    color: #555555;
    margin-left: 4px;
  }

  .userPreview {
    padding-left: 10px;
  }

  .notification {
    p {
      margin: 0;
      text-align: left;
    }
  }
</style>
