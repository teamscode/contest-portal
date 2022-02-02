<template>
  <div>
    <Form
      ref="formRegister"
      :model="formRegister"
      :rules="ruleRegister"
    >
      <Row type="flex" align="middle">
        <Col
          span="12"
          style="padding-right: 10px"
        >
          <FormItem prop="username">
            <Input
              v-model="formRegister.username"
              type="text"
              :placeholder="$t('m.RegisterUsername')"
              size="large"
              @on-enter="handleRegister"
            >
              <Icon
                slot="prepend"
                type="ios-person-outline"
              />
            </Input>
          </FormItem>
          <FormItem prop="password">
            <Input
              v-model="formRegister.password"
              type="password"
              :placeholder="$t('m.RegisterPassword')"
              size="large"
              @on-enter="handleRegister"
            >
              <Icon
                slot="prepend"
                type="ios-lock-outline"
              />
            </Input>
          </FormItem>
          <FormItem prop="passwordAgain">
            <Input
              v-model="formRegister.passwordAgain"
              type="password"
              :placeholder="$t('m.Password_Again')"
              size="large"
              @on-enter="handleRegister"
            >
              <Icon
                slot="prepend"
                type="ios-lock-outline"
              />
            </Input>
          </FormItem>
          <FormItem prop="team_name">
            <Input
              v-model="formRegister.team_name"
              type="text"
              placeholder="Team Name"
              size="large"
              @on-enter="handleRegister"
            >
              <Icon
                slot="prepend"
                type="ios-people-outline"
              />
            </Input>
          </FormItem>
          <FormItem prop="division">
            <span>Contest Division (can be changed later)</span>
            <Select v-model="formRegister.division" size="large" style="max-width: 120px; position: absolute; right: 0px">
              <Option v-for="item in CONTEST_DIVISIONS" :value="item" :key="item">{{ item }}</Option>
            </Select>
          </FormItem>
          <FormItem prop="membersCount">
            <span>Number of Team Members</span>
            <InputNumber
              v-model="formRegister.membersCount"
              style="position: absolute; right: 0px"
              :max="4"
              :min="1"
              size="large"
              @on-enter="handleRegister"
              @on-change="changeMembersCount"
            />
          </FormItem>
          <FormItem
            prop="captcha"
            style="margin-bottom: 10px"
          >
            <div class="oj-captcha">
              <div class="oj-captcha-code">
                <Input
                  v-model="formRegister.captcha"
                  :placeholder="$t('m.Captcha')"
                  size="large"
                  @on-enter="handleRegister"
                >
                  <Icon
                    slot="prepend"
                    type="ios-bulb-outline"
                  />
                </Input>
              </div>
              <div class="oj-captcha-img">
                <Tooltip
                  content="Click to refresh"
                  placement="top"
                >
                  <img
                    :src="captchaSrc"
                    @click="getCaptchaSrc"
                  >
                </Tooltip>
              </div>
            </div>
          </FormItem>
        </Col>
        <Col span="12">
          <div
            v-for="(member, index) in formRegister.team_members"
            :key="index"
          >
            <div style="margin-bottom: 10px; margin-top: 10px">
              Team Member #{{ index + 1 }} Information <span v-if="index===0">(captain)</span>
            </div>
            <Row>
                <Col span="18">
                  <FormItem
                    :prop="'team_members.' + index + '.name'"
                    :rules="{ required: true, trigger: 'blur', max: 64 }"
                  >
                    <Input
                      v-model="formRegister.team_members[index].name"
                      type="text"
                      :placeholder="'Name'"
                      size="large"
                      @on-enter="handleRegister"
                    >
                      <Icon
                        slot="prepend"
                        type="ios-person-outline"
                      />
                    </Input>
                  </FormItem>
                </Col>
                <Col span="5" offset="1" style="padding-left: 9px">
                    <FormItem
                    :prop="'team_members.' + index + '.year'"
                    :rules="{ required: true, type: 'number', min: 1900, max: 2100, message: 'invalid' }"
                    >
                      <Tooltip content="High school graduation year">
                        <InputNumber
                          v-model.number="formRegister.team_members[index].year"
                          type="text"
                          :placeholder="'Class'"
                          size="large"
                          @on-enter="handleRegister"
                        >
                        </InputNumber>
                      </Tooltip>
                    </FormItem>
                </Col>
            </Row>
            <FormItem
              :prop="'team_members.' + index + '.email'"
              style="padding-top: 0px"
              :rules="
                index === 0
                  ? [
                    { required: true, type: 'email', trigger: 'blur', max: 64 },
                    { validator: CheckEmailNotExist, trigger: 'blur' },
                  ]
                  : { required: true, type: 'email', trigger: 'blur', max: 64}
              "
            >
              <Input
                v-model="formRegister.team_members[index].email"
                type="text"
                :placeholder="'Team Member ' + (index + 1) + ' Email'"
                size="large"
                @on-enter="handleRegister"
              >
                <Icon
                  slot="prepend"
                  type="ios-mail-outline"
                />
              </Input>
            </FormItem>
          </div>
        </Col>
      </Row>
    </Form>
    <div class="footer">
      <Button
        type="primary"
        class="btn"
        long
        :loading="btnRegisterLoading"
        @click="handleRegister"
      >
        {{ $t("m.UserRegister") }}
      </Button>
      <Button
        class="btn"
        long
        @click="switchMode('login')"
      >
        {{ $t("m.Already_Registed") }}
      </Button>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import api from '@oj/api'
import { FormMixin } from '@oj/components/mixins'
import { CONTEST_DIVISIONS } from '@/utils/constants'

export default {
  mixins: [FormMixin],
  data () {
    return {
      btnRegisterLoading: false,
      formRegister: {
        username: '',
        password: '',
        team_name: '',
        membersCount: 1,
        passwordAgain: '',
        captcha: '',
        division: '',
        team_members: [{ name: '', email: '', year: null }]
      },
      ruleRegister: {
        username: [
          { required: true, trigger: 'blur', max: 64 },
          { validator: this.CheckUsernameNotExist, trigger: 'blur' }
        ],
        password: [
          { required: true, trigger: 'blur', min: 6, max: 20 },
          { validator: this.CheckPassword, trigger: 'blur' }
        ],
        passwordAgain: [
          {
            required: true,
            validator: this.CheckAgainPassword,
            trigger: 'change'
          }
        ],
        captcha: [{ required: true, trigger: 'blur', min: 1, max: 10 }],
        membersCount: [
          { required: true, type: 'number', trigger: 'blur', min: 1, max: 4 }
        ],
        team_name: [
          { required: true, trigger: 'blur', max: 128 },
          { validator: this.CheckTeamnameNotExist, trigger: 'blur' }
        ],
        division: [
          { required: true }
        ]
      }
    }
  },
  mounted () {
    this.getCaptchaSrc()
  },
  methods: {
    ...mapActions(['changeModalStatus', 'getProfile']),
    CheckEmailNotExist (rule, value, callback) {
      api.checkUsernameOrEmail(undefined, value, undefined).then(
        (res) => {
          if (res.data.data.email === true) {
            callback(new Error(this.$i18n.t('m.The_email_already_exists')))
          } else {
            callback()
          }
        },
        (_) => callback()
      )
    },
    CheckUsernameNotExist (rule, value, callback) {
      api.checkUsernameOrEmail(value, undefined, undefined).then(
        (res) => {
          if (res.data.data.username === true) {
            callback(new Error(this.$i18n.t('m.The_username_already_exists')))
          } else {
            callback()
          }
        },
        (_) => callback()
      )
    },
    CheckTeamnameNotExist (rule, value, callback) {
      api.checkUsernameOrEmail(undefined, undefined, value).then(
        (res) => {
          if (res.data.data.team_name === true) {
            callback(new Error('This team name already exists'))
          } else {
            callback()
          }
        },
        (_) => callback()
      )
    },
    CheckPassword (rule, value, callback) {
      if (this.formRegister.password !== '') {
        // 对第二个密码框再次验证
        this.$refs.formRegister.validateField('passwordAgain')
      }
      callback()
    },
    CheckAgainPassword (rule, value, callback) {
      if (value !== this.formRegister.password) {
        callback(new Error(this.$i18n.t('m.password_does_not_match')))
      }
      callback()
    },
    switchMode (mode) {
      this.changeModalStatus({
        mode,
        visible: true
      })
    },
    changeMembersCount () {
      this.formRegister.team_members.splice(this.formRegister.membersCount)
      while (
        this.formRegister.team_members.length < this.formRegister.membersCount
      ) {
        this.formRegister.team_members.push({ name: '', email: '', year: null })
      }
    },
    handleRegister () {
      this.validateForm('formRegister').then((valid) => {
        let formData = Object.assign({}, this.formRegister)
        delete formData['passwordAgain']
        formData['email'] = formData['team_members'][0].email
        this.btnRegisterLoading = true
        api.register(formData).then(
          (res) => {
            this.$success(this.$i18n.t('m.Thanks_for_registering'))
            this.switchMode('login')
            this.btnRegisterLoading = false
          },
          (_) => {
            this.getCaptchaSrc()
            this.formRegister.captcha = ''
            this.btnRegisterLoading = false
          }
        )
      })
    }
  },
  computed: {
    ...mapGetters(['website', 'modalStatus']),
    CONTEST_DIVISIONS () {
      return CONTEST_DIVISIONS
    }
  }
}
</script>

<style scoped lang="less">
.footer {
  overflow: auto;
  margin-top: 20px;
  margin-bottom: -15px;
  text-align: left;
  .btn {
    margin: 0 0 15px 0;
    &:last-child {
      margin: 0;
    }
  }
}
</style>
