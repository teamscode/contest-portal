<template>
  <div>
    <div class="setting-main">
      <div class="section-title">Team Profile</div>
      <Alert show-icon v-if="!website.allow_register">Cannot modify team after registration deadline</Alert>
      <Form ref="formProfile" :model="formProfile" :rules="ruleProfile" :disabled="!website.allow_register">
        <Row type="flex" :gutter="30" justify="space-around">
          <Col :span="11">
            <FormItem prop="team_name" label="Team Name">
              <Input
                v-model="formProfile.team_name"
                type="text"
              >
              </Input>
            </FormItem>
            <FormItem prop="division">
              <span>Contest Division</span>
              <Select v-model="formProfile.division" style="max-width: 120px; position: absolute; right: 0px">
                <Option v-for="item in CONTEST_DIVISIONS" :value="item" :key="item">{{ item }}</Option>
              </Select>
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
              <Row>
                <Col span="16">
                  <FormItem
                    :prop="'team_members.' + index + '.name'"
                    :label="index === 0 ? 'Captain\'s Name' : 'Team Member ' + (index + 1) + ' Name'"
                    :rules="{ required: true, trigger: 'blur', max: 64 }"
                  >
                    <Input
                      v-model="formProfile.team_members[index].name"
                      type="text"
                    >
                    </Input>
                  </FormItem>
                </Col>
                <Col span="8">
                  <FormItem
                    :prop="'team_members.' + index + '.year'"
                    :label="'Class'"
                    :rules="{ required: true, type: 'number', min: 1900, max: 2100 }"
                  >
                    <Tooltip content="High school graduation year" style="margin-left: 8px; width: 100%">
                      <InputNumber
                        style="width: 96%; margin-right: 3px"
                        v-model.number="formProfile.team_members[index].year"
                        type="text"
                      >
                      </InputNumber>
                    </Tooltip>
                  </FormItem>
                </Col>
              </Row>
              <FormItem
                :prop="'team_members.' + index + '.email'"
                :label="index === 0 ? 'Captain\'s Email' : 'Team Member ' + (index + 1) + ' Email'"
                :rules="{ required: true, type: 'email', trigger: 'blur', max: 64}"
              >
                <Input
                  v-model="formProfile.team_members[index].email"
                  :disabled="index===0"
                  type="text"
                >
                </Input>
                <div v-if="index===0">Captain's email can be changed in the Account tab</div>
              </FormItem>
              <FormItem
                :prop="'team_members.' + index + '.parent_email'"
                :label="index === 0 ? 'Captain\'s Parent Email' : 'Team Member ' + (index + 1) + ' Parent Email'"
                :rules="{ required: true, type: 'email', trigger: 'blur', max: 64}"
              >
                <Input
                  v-model="formProfile.team_members[index].parent_email"
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
  import { CONTEST_DIVISIONS } from '@/utils/constants'

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
          membersCount: 1,
          division: ''
        },
        ruleProfile: {
          team_name: [
            { required: true, trigger: 'blur', max: 128 }
          ],
          division: [
            { required: true }
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
        loadedProfile.division = this.profile.division
        loadedProfile.team_members = JSON.parse(JSON.stringify(this.profile.team_members))
        loadedProfile.membersCount = this.profile.team_members.length
        this.formProfile = loadedProfile
      },
      updateProfile () {
        this.validateForm('formProfile').then((valid) => {
          this.loadingSaveBtn = true
          let updateData = utils.filterEmptyValue(Object.assign({}, this.formProfile))
          api.updateProfile(updateData).then(res => {
            this.$success('Saved')
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
          this.formProfile.team_members.push({ name: '', email: '', year: null, parent_email: '' })
        }
      }
    },
    computed: {
      ...mapGetters(['profile', 'website']),
      CONTEST_DIVISIONS () {
        return CONTEST_DIVISIONS
      }
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
