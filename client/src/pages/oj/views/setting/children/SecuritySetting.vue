<template>
  <div>
    <div class="setting-main">
      <p class="section-title">
        {{ $t('m.Sessions') }}
      </p>
      <Row>
        <Col v-for="session in sessions" :key="session.session_key" style="padding: 5px">
          <Card
            :key="session.ip"
          >
            <span
              slot="title"
              style="line-height: 20px"
            >{{ session.ip }}</span>
            <div slot="extra">
              <Tag
                v-if="session.current_session"
                color="green"
              >
                Current
              </Tag>
              <Button
                v-else
                type="warning"
                size="small"
                @click="deleteSession(session.session_key)"
              >
                Revoke
              </Button>
            </div>
            <Form :label-width="100">
              <FormItem
                label="OS :"
                class="item"
              >
                {{ session.user_agent | platform }}
              </FormItem>
              <FormItem
                label="Browser :"
                class="item"
              >
                {{ session.user_agent | browser }}
              </FormItem>
              <FormItem
                label="Last Activity :"
                class="item"
              >
                {{ session.last_activity | localtime }}
              </FormItem>
            </Form>
          </Card>
        </Col>
      </Row>

      <Divider />
      <p class="section-title">
        {{ $t('m.Two_Factor_Authentication') }}
      </p>
      <div class="mini-container setting-content">
        <Form>
          <Alert
            v-if="TFAOpened"
            type="success"
            class="notice"
            show-icon
          >
            You have enabled two-factor authentication
          </Alert>
          <FormItem v-if="!TFAOpened">
            <div class="oj-relative">
              <img
                id="qr-img"
                :src="qrcodeSrc"
              >
              <Spin
                v-if="loadingQRcode"
                size="large"
                fix
              />
            </div>
          </FormItem>
          <template v-if="!loadingQRcode">
            <Row>
              <FormItem style="width: 200px;">
                <Input
                  v-model="formTwoFactor.code"
                  style="margin-bottom: 2px"
                  placeholder="Code from your TFA app"
                />
              </FormItem>
              <Button
                v-if="!TFAOpened"
                type="primary"
                :loading="loadingBtn"
                @click="updateTFA(false)"
                style="margin-left: 10px"
              >
                Enable TFA
              </Button>
              <Button
                v-else
                type="error"
                style="margin-left: 10px"
                :loading="loadingBtn"
                @click="closeTFA"
              >
                Disable TFA
              </Button>
            </Row>
          </template>
        </Form>
      </div>
    </div>
  </div>
</template>

<script>
  import api from '@oj/api'
  import {mapGetters, mapActions} from 'vuex'
  import browserDetector from 'browser-detect'

  const browsers = {}
  const loadBrowser = (userAgent) => {
    let browser = {}
    if (userAgent in Object.keys(browsers)) {
      browser = browsers[userAgent]
    } else {
      browser = browserDetector(userAgent)
      browsers[userAgent] = browser
    }
    return browser
  }

  export default {
    data () {
      return {
        qrcodeSrc: '',
        loadingQRcode: false,
        loadingBtn: false,
        formTwoFactor: {
          code: ''
        },
        sessions: []
      }
    },
    mounted () {
      this.getSessions()
      if (!this.TFAOpened) {
        this.getAuthImg()
      }
    },
    methods: {
      ...mapActions(['getProfile']),
      getAuthImg () {
        this.loadingQRcode = true
        api.twoFactorAuth('get').then(res => {
          this.loadingQRcode = false
          this.qrcodeSrc = res.data.data
        })
      },
      getSessions () {
        api.getSessions().then(res => {
          let data = res.data.data
          // 将当前session放到第一个
          let sessions = data.filter(session => {
            return session.current_session
          })
          data.forEach(session => {
            if (!session.current_session) {
              sessions.push(session)
            }
          })
          this.sessions = sessions
        })
      },
      deleteSession (sessionKey) {
        this.$Modal.confirm({
          title: 'Confirm',
          content: 'Are you sure to revoke the session?',
          onOk: () => {
            api.deleteSession(sessionKey).then(res => {
              this.getSessions()
            }, _ => {
            })
          }
        })
      },
      closeTFA () {
        this.$Modal.confirm({
          title: 'Confirm',
          content: 'Two-factor Authentication is a powerful tool to protect your account, are you sure to close it?',
          onOk: () => {
            this.updateTFA(true)
          }
        })
      },
      updateTFA (close) {
        let method = close === false ? 'post' : 'put'
        this.loadingBtn = true
        api.twoFactorAuth(method, this.formTwoFactor).then(res => {
          this.loadingBtn = false
          this.getProfile()
          if (close === true) {
            this.getAuthImg()
            this.formTwoFactor.code = ''
          }
          this.formTwoFactor.code = ''
        }, err => {
          this.formTwoFactor.code = ''
          this.loadingBtn = false
          if (err.data.data.indexOf('session') > -1) {
            this.getProfile()
            this.getAuthImg()
          }
        })
      }
    },
    computed: {
      ...mapGetters(['user']),
      TFAOpened () {
        return this.user && this.user.two_factor_auth
      }
    },
    filters: {
      browser (value) {
        let b = loadBrowser(value)
        if (b.name && b.version) {
          return b.name + ' ' + b.version
        } else {
          return 'Unknown'
        }
      },
      platform (value) {
        let b = loadBrowser(value)
        return b.os ? b.os : 'Unknown'
      }
    }
  }
</script>

<style lang="less" scoped>
  .notice {
    margin-bottom: 20px;
    display: inline-block;
  }

  .oj-relative {
    width: 150px;
    #qr-img {
      width: 300px;
      margin: -10px 0 -30px -20px;
    }
  }
</style>
