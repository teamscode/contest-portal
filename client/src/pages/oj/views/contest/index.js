const ContestList = () => import(/* webpackChunkName: "contest" */ './ContestList.vue')
const ContestDetails = () => import(/* webpackChunkName: "contest" */ './ContestDetail.vue')
const ContestProblemList = () => import(/* webpackChunkName: "contest" */ './children/ContestProblemList.vue')
const ContestRank = () => import(/* webpackChunkName: "contest" */ './children/ContestRank.vue')
const ContestRankReview = () => import(/* webpackChunkName: "contest" */ './children/ContestRankReview.vue')
const ContestReview = () => import(/* webpackChunkName: "contest" */ './children/ContestReview.vue')

export {ContestDetails, ContestList, ContestProblemList, ContestRank, ContestRankReview, ContestReview}
