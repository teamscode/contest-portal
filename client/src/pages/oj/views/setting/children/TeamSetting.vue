<template>
  <div>
    <div class="setting-main">
      <div class="section-title">Team Profile</div>
      <Form ref="formProfile" :model="formProfile" :rules="ruleProfile">
        <Row type="flex" :gutter="30" justify="space-around">
          <Col :span="11">
            <FormItem prop="team_name" label="Team Name">
              <Input
                v-model="formProfile.team_name"
                type="text"
              >
              </Input>
            </FormItem>
            <FormItem prop="membersCount">
              <span>Number of Team Members</span>
              <InputNumber
                v-model="formProfile.membersCount"
                style="position: absolute; right: 0px"
                :max="4"
                :min="1"
                :rules="{ required: true, trigger: 'blur', min: 1, max: 4 }"
                @on-change="changeMembersCount"
              />
            </FormItem>
            <Form-item>
              <Button type="primary" @click="updateProfile" :loading="loadingSaveBtn">Save All</Button>
            </Form-item>
          </Col>


          <Col :span="11">
            <div
              v-for="(member, index) in formProfile.team_members"
              :key="index"
            >
              <FormItem
                :prop="'team_members.' + index + '.name'"
                :label="'Team Member ' + (index + 1) + ' Name'"
                :rules="{ required: true, trigger: 'blur', max: 64 }"
              >
                <Input
                  v-model="formProfile.team_members[index].name"
                  type="text"
                >
                </Input>
              </FormItem>
              <FormItem
                :prop="'team_members.' + index + '.email'"
                :label="'Team Member ' + (index + 1) + ' Email'"
                :rules="
                  index === 0
                    ? [
                      { required: true, type: 'email', trigger: 'blur', max: 64 },
                    ]
                    : { required: true, type: 'email', trigger: 'blur', max: 64}
                "
              >
                <Input
                  v-model="formProfile.team_members[index].email"
                  type="text"
                >
                </Input>
              </FormItem>
            </div>
          </Col>
        </Row>
      </Form>
    </div>
  </div>
</template>

<script>
  import api from '@oj/api'
  import utils from '@/utils/utils'
  import {VueCropper} from 'vue-cropper'
  import {types} from '@/store'
  import {languages} from '@/i18n'
  import { FormMixin } from '@oj/components/mixins'
  import { mapGetters } from 'vuex'

  export default {
    mixins: [FormMixin],
    components: {
      VueCropper
    },
    data () {
      return {
        loadingSaveBtn: false,
        loadingUploadBtn: false,

        languages: languages,
        formProfile: {
          team_name: '',
          team_members: [],
          membersCount: 1
        },
        ruleProfile: {
          team_name: [
            { required: true, trigger: 'blur', max: 128 }
          ]
        }
      }
    },
    mounted () {
      if (this.profile && this.profile.team_name) {
        this.loadProfile()
      }
    },
    methods: {
      loadProfile () {
        let loadedProfile = {}
        loadedProfile.team_name = this.profile.team_name
        loadedProfile.team_members = JSON.parse(JSON.stringify(this.profile.team_members))
        loadedProfile.membersCount = this.profile.team_members.length
        this.formProfile = loadedProfile
      },
      updateProfile () {
        this.validateForm('formProfile').then((valid) => {
          this.loadingSaveBtn = true
          let updateData = utils.filterEmptyValue(Object.assign({}, this.formProfile))
          api.updateProfile(updateData).then(res => {
            this.$success('Success')
            this.$store.commit(types.CHANGE_PROFILE, {profile: res.data.data})
            this.loadingSaveBtn = false
          }, _ => {
            this.loadingSaveBtn = false
          })
        })
      },
      changeMembersCount () {
        this.formProfile.team_members.splice(this.formProfile.membersCount)
        while (
        this.formProfile.team_members.length < this.formProfile.membersCount
      ) {
          this.formProfile.team_members.push({ name: '', email: '' })
        }
      }
    },
    computed: {
      ...mapGetters(['profile'])
    },
    watch: {
      profile () {
        if (this.profile && this.profile.team_name) {
          this.loadProfile()
        }
      }
    }
  }
</script>

<style lang="less" scoped>
  .inline {
    display: inline-block;
  }
</style>
