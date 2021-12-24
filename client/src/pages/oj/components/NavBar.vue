<template>
  <div id="header">
    <Menu
      theme="light"
      mode="horizontal"
      :active-name="activeMenu"
      class="oj-menu"
      @on-select="handleRoute"
    >
      <div class="logoimg">
        <img
          src="../../../assets/logo.svg"
          alt="oj logo"
        >
      </div>
      <div class="logo">
        <span>{{ website.website_name }}</span>
      </div>
      <Menu-item name="/">
        <Icon type="home" />
        {{ $t('m.Home') }}
      </Menu-item>
      <Submenu
        v-if="isAdminRole"
        name="problem"
      >
        <template slot="title">
          <Icon type="ios-keypad" />
          {{ $t('m.NavProblems') }}
        </template>
        <Menu-item name="/problem">
          {{ $t('m.Problem_List') }}
        </Menu-item>
        <Menu-item name="/status">
          {{ $t('m.Submissions') }}
        </Menu-item>
      </Submenu>
      <Menu-item name="/contest">
        <Icon type="trophy" />
        {{ $t('m.Contests') }}
      </Menu-item>
      <Submenu name="about">
        <template slot="title">
          <Icon type="information-circled" />
          {{ $t('m.About') }}
        </template>
        <Menu-item name="/judger">
          {{ $t('m.Judger') }}
        </Menu-item>
        <Menu-item name="/FAQ">
          {{ $t('m.FAQ') }}
        </Menu-item>
      </Submenu>
      <template v-if="!isAuthenticated">
        <div class="btn-menu">
          <Button
            ref="loginBtn"
            type="ghost"
            shape="circle"
            @click="handleBtnClick('login')"
          >
            {{ $t('m.Login') }}
          </Button>
          <Button
            v-if="website.allow_register"
            type="ghost"
            shape="circle"
            style="margin-left: 5px;"
            @click="handleBtnClick('register')"
          >
            {{ $t('m.Register') }}
          </Button>
        </div>
      </template>
      <template v-else>
        <Dropdown
          class="drop-menu"
          placement="bottom"
          trigger="click"
          @on-click="handleRoute"
        >
          <Button
            type="text"
            class="drop-menu-title"
          >
            {{ user.username }}
            <Icon type="arrow-down-b" />
          </Button>
          <Dropdown-menu slot="list">
            <Dropdown-item name="/setting/account">
              {{ $t('m.Settings') }}
            </Dropdown-item>
            <Dropdown-item
              v-if="isAdminRole"
              name="/admin"
            >
              {{ $t('m.Management') }}
            </Dropdown-item>
            <Dropdown-item
              divided
              name="/logout"
            >
              {{ $t('m.Logout') }}
            </Dropdown-item>
          </Dropdown-menu>
        </Dropdown>
      </template>
    </Menu>
    <Modal
      v-model="modalVisible"
      :width="modalStatus.mode==='register'?800:400"
    >
      <div
        slot="header"
        class="modal-title"
      >
        {{ website.website_name }}
      </div>
      <component
        :is="modalStatus.mode"
        v-if="modalVisible"
      />
      <div
        slot="footer"
        style="display: none"
      />
    </Modal>
  </div>
</template>

<script>
  import { mapGetters, mapActions } from 'vuex'
  import login from '@oj/views/user/Login'
  import register from '@oj/views/user/Register'

  export default {
    components: {
      login,
      register
    },
    mounted () {
      this.getProfile()
    },
    methods: {
      ...mapActions(['getProfile', 'changeModalStatus']),
      handleRoute (route) {
        if (route && route.indexOf('admin') < 0) {
          this.$router.push(route)
        } else {
          window.open('/admin/')
        }
      },
      handleBtnClick (mode) {
        this.changeModalStatus({
          visible: true,
          mode: mode
        })
      }
    },
    computed: {
      ...mapGetters(['website', 'modalStatus', 'user', 'isAuthenticated', 'isAdminRole']),
      // 跟随路由变化
      activeMenu () {
        return '/' + this.$route.path.split('/')[1]
      },
      modalVisible: {
        get () {
          return this.modalStatus.visible
        },
        set (value) {
          this.changeModalStatus({visible: value})
        }
      }
    }
  }
</script>

<style lang="less" scoped>
  #header {
    min-width: 300px;
    position: fixed;
    top: 0;
    left: 0;
    height: auto;
    width: 100%;
    z-index: 1000;
    background-color: #fff;
    box-shadow: 0 1px 5px 0 rgba(0, 0, 0, 0.1);
    .oj-menu {
      background: #fdfdfd;
    }

    .logo {
      margin-left: 15px;
      margin-right: 2%;
      font-size: 20px;
      float: left;
      line-height: 60px;
    }

    .logoimg {
      float: left;
      width: 35px;
      margin-top: 12px;
      margin-left: 2%;
      height: 35px;
    }

    .drop-menu {
      float: right;
      margin-right: 30px;
      position: absolute;
      right: 10px;
      &-title {
        font-size: 18px;
      }
    }
    .btn-menu {
      font-size: 16px;
      float: right;
      margin-right: 10px;
    }
  }

  .modal {
    &-title {
      font-size: 18px;
      font-weight: 600;
    }
  }
</style>
