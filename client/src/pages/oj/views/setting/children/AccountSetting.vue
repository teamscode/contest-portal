<template>
  <div>
    <div class="setting-main">
      <div class="flex-container">
        <div class="left">
          <p class="section-title">
            {{ $t('m.ChangePassword') }}
          </p>
          <Form
            ref="formPassword"
            class="setting-content"
            :model="formPassword"
            :rules="rulePassword"
          >
            <FormItem
              label="Current Password"
              prop="old_password"
            >
              <Input
                v-model="formPassword.old_password"
                type="password"
              />
            </FormItem>
            <FormItem
              label="New Password"
              prop="new_password"
            >
              <Input
                v-model="formPassword.new_password"
                type="password"
              />
            </FormItem>
            <FormItem
              label="Confirm New Password"
              prop="again_password"
            >
              <Input
                v-model="formPassword.again_password"
                type="password"
              />
            </FormItem>
            <FormItem
              v-if="visible.tfaRequired"
              label="Two Factor Auth"
              prop="tfa_code"
            >
              <Input v-model="formPassword.tfa_code" />
            </FormItem>
            <FormItem v-if="visible.passwordAlert">
              <Alert type="success">
                You will need to login again with the new credential after 5 seconds.
              </Alert>
            </FormItem>
            <Button
              type="primary"
              :loading="loading.btnPassword"
              @click="changePassword"
            >
              {{ $t('m.Update_Password') }}
            </Button>
          </Form>
        </div>

        <div class="middle separator" />

        <div class="right">
          <p class="section-title">
            {{ $t('m.ChangeEmail') }}
          </p>
          <Alert show-icon v-if="!website.allow_register">Cannot update email after registration deadline</Alert>
          <Form
            ref="formEmail"
            class="setting-content"
            :model="formEmail"
            :rules="ruleEmail"
            :disabled="!website.allow_register"
          >
            <FormItem
              label="Current Password"
              prop="password"
            >
              <Input
                v-model="formEmail.password"
                type="password"
              />
            </FormItem>
            <FormItem label="Current Email">
              <Input
                v-model="user.email"
                disabled
              />
            </FormItem>
            <FormItem
              label="New Email"
              prop="new_email"
            >
              <Input v-model="formEmail.new_email" />
            </FormItem>
            <FormItem
              v-if="visible.tfaRequired"
              label="Two Factor Auth"
              prop="tfa_code"
            >
              <Input v-model="formEmail.tfa_code" />
            </FormItem>
            <Button
              type="primary"
              @click="changeEmail"
              :loading="loading.btnEmail"
            >
              {{ $t('m.ChangeEmail') }}
            </Button>
          </Form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import api from '@oj/api'
  import { mapGetters, mapActions } from 'vuex'
  import { FormMixin } from '@oj/components/mixins'

  export default {
    mixins: [FormMixin],
    data () {
      const oldPasswordCheck = [{required: true, trigger: 'blur', min: 6, max: 20}]
      const tfaCheck = [{required: true, trigger: 'change'}]
      const CheckAgainPassword = (rule, value, callback) => {
        if (value !== this.formPassword.new_password) {
          callback(new Error('password does not match'))
        }
        callback()
      }
      const CheckNewPassword = (rule, value, callback) => {
        if (this.formPassword.old_password !== '') {
          if (this.formPassword.old_password === this.formPassword.new_password) {
            callback(new Error('The new password doesn\'t change'))
          } else {
            // 对第二个密码框再次验证
            this.$refs.formPassword.validateField('again_password')
          }
        }
        callback()
      }
      return {
        loading: {
          btnPassword: false,
          btnEmail: false
        },
        visible: {
          passwordAlert: false,
          emailAlert: false,
          tfaRequired: false
        },
        formPassword: {
          tfa_code: '',
          old_password: '',
          new_password: '',
          again_password: ''
        },
        formEmail: {
          tfa_code: '',
          password: '',
          new_email: ''
        },
        rulePassword: {
          old_password: oldPasswordCheck,
          new_password: [
            {required: true, trigger: 'blur', min: 6, max: 20},
            {validator: CheckNewPassword, trigger: 'blur'}
          ],
          again_password: [
            {required: true, validator: CheckAgainPassword, trigger: 'change'}
          ],
          tfa_code: tfaCheck
        },
        ruleEmail: {
          password: oldPasswordCheck,
          new_email: [{required: true, type: 'email', trigger: 'change'}],
          tfa_code: tfaCheck
        }
      }
    },
    methods: {
      ...mapActions(['getProfile']),
      changePassword () {
        this.validateForm('formPassword').then(valid => {
          this.loading.btnPassword = true
          let data = Object.assign({}, this.formPassword)
          delete data.again_password
          if (!this.visible.tfaRequired) {
            delete data.tfa_code
          }
          api.changePassword(data).then(res => {
            this.loading.btnPassword = false
            this.visible.passwordAlert = true
            this.$success('Password Updated')
            setTimeout(() => {
              this.visible.passwordAlert = false
              this.$router.push({name: 'logout'})
            }, 5000)
          }, res => {
            if (res.data.data === 'tfa_required') {
              this.visible.tfaRequired = true
            }
            this.loading.btnPassword = false
          })
        })
      },
      changeEmail () {
        this.validateForm('formEmail').then(valid => {
          this.loading.btnEmail = true
          let data = Object.assign({}, this.formEmail)
          if (!this.visible.tfaRequired) {
            delete data.tfa_code
          }
          api.changeEmail(data).then(res => {
            this.loading.btnEmail = false
            this.visible.emailAlert = true
            this.$success('Email Updated')
            this.getProfile()
            this.$refs.formEmail.resetFields()
          }, res => {
            if (res.data.data === 'tfa_required') {
              this.visible.tfaRequired = true
            }
          })
        })
      }
    },
    computed: {
      ...mapGetters(['user', 'website'])
    }
  }
</script>

<style lang="less" scoped>

  .flex-container {
    justify-content: flex-start;
    .left {
      flex: 1 0;
      width: 250px;
      padding-right: 5%;
    }
    > .middle {
      flex: none;
    }
    .right {
      flex: 1 0;
      width: 250px;
    }
  }
</style>

