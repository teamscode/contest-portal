<template>
  <div>
    <Panel
      :padding="30"
      shadow
      class="container"
    >
      <div
        slot="title"
        class="center"
      >
        {{ $t('m.Reset_Password') }}
      </div>
      <template v-if="!resetSuccess">
        <Form
          ref="formResetPassword"
          :model="formResetPassword"
          :rules="ruleResetPassword"
        >
          <Form-item prop="password">
            <Input
              v-model="formResetPassword.password"
              type="password"
              :placeholder="$t('m.RPassword')"
              size="large"
            >
              <Icon
                slot="prepend"
                type="ios-lock-outline"
              />
            </Input>
          </Form-item>
          <Form-item prop="passwordAgain">
            <Input
              v-model="formResetPassword.passwordAgain"
              type="password"
              :placeholder="$t('m.RPassword_Again')"
              size="large"
            >
              <Icon
                slot="prepend"
                type="ios-lock-outline"
              />
            </Input>
          </Form-item>
          <Form-item
            prop="captcha"
            style="margin-bottom:10px"
          >
            <div id="captcha">
              <div id="captchaCode">
                <Input
                  v-model="formResetPassword.captcha"
                  :placeholder="$t('m.RCaptcha')"
                  size="large"
                >
                  <Icon
                    slot="prepend"
                    type="ios-bulb-outline"
                  />
                </Input>
              </div>
              <div id="captchaImg">
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
          </Form-item>
        </Form>
        <Button
          type="primary"
          class="btn"
          long
          :loading="btnLoading"
          @click="resetPassword"
        >
          {{ $t('m.Reset_Password') }}
        </Button>
      </template>

      <template v-else>
        <Alert type="success">
          {{ $t('m.Your_password_has_been_reset') }}
        </Alert>
      </template>
    </Panel>
  </div>
</template>

<script>
  import {FormMixin} from '@oj/components/mixins'
  import api from '@oj/api'

  export default {
    name: 'ResetPassword',
    mixins: [FormMixin],
    data () {
      const CheckPassword = (rule, value, callback) => {
        if (this.formResetPassword.passwdCheck !== '') {
          // 对第二个密码框再次验证
          this.$refs.formResetPassword.validateField('passwordAgain')
        }
        callback()
      }

      const CheckAgainPassword = (rule, value, callback) => {
        if (value !== this.formResetPassword.password) {
          callback(new Error(this.$i18n.t('m.password_does_not_match')))
        }
        callback()
      }
      return {
        btnLoading: false,
        captchaSrc: '',
        resetSuccess: false,
        formResetPassword: {
          captcha: '',
          password: '',
          passwordAgain: '',
          token: ''
        },
        ruleResetPassword: {
          password: [
            {required: true, trigger: 'blur', min: 6, max: 20},
            {validator: CheckPassword, trigger: 'blur'}
          ],
          passwordAgain: [
            {required: true, validator: CheckAgainPassword, trigger: 'change'}
          ],
          captcha: [
            {required: true, trigger: 'blur', min: 1, max: 10}
          ]
        }
      }
    },
    mounted () {
      this.formResetPassword.token = this.$route.params.token
      this.getCaptchaSrc()
    },
    methods: {
      resetPassword () {
        this.validateForm('formResetPassword').then(valid => {
          this.btnLoading = true
          let data = Object.assign({}, this.formResetPassword)
          delete data.passwordAgain
          api.resetPassword(data).then(res => {
            this.btnLoading = false
            this.resetSuccess = true
          }, _ => {
            this.btnLoading = false
            this.formResetPassword.captcha = ''
            this.getCaptchaSrc()
          })
        })
      }
    }
  }
</script>
<style lang="less" scoped>
  .container {
    width: 450px;
    margin: auto;
    .center {
      text-align: center;
    }
    #captcha {
      display: flex;
      flex-wrap: nowrap;
      justify-content: space-between;
      width: 100%;
      height: 36px;
      #captchaCode {
        flex: auto;
      }
      #captchaImg {
        margin-left: 10px;
        padding: 3px;
        flex: initial;
      }
    }
    .btn {
      margin-top: 18px;
      text-align: center;
    }
  }
</style>
