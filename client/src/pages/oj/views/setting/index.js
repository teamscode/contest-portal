const Settings = () => import(/* webpackChunkName: "setting" */ './Settings.vue')
const SecuritySetting = () => import(/* webpackChunkName: "setting" */ './children/SecuritySetting.vue')
const AccountSetting = () => import(/* webpackChunkName: "setting" */ './children/AccountSetting.vue')
const TeamSetting = () => import(/* webpackChunkName: "setting" */ './children/TeamSetting.vue')

export {Settings, SecuritySetting, AccountSetting, TeamSetting}
