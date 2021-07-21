const Settings = () => import(/* webpackChunkName: "setting" */ './Settings.vue')
const SecuritySetting = () => import(/* webpackChunkName: "setting" */ './children/SecuritySetting.vue')
const AccountSetting = () => import(/* webpackChunkName: "setting" */ './children/AccountSetting.vue')

export {Settings, SecuritySetting, AccountSetting}
