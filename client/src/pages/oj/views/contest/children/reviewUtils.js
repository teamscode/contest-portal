export const VOTE_VOLUME_N = 5 // total effective votes at which the confidence bar reads "full"

export function getEffectiveUpvotes (user) {
  return (user.upvotes || 0) + (user.has_culv_flag ? 10 : 0)
}

export function getVoteRatio (user) {
  const up = getEffectiveUpvotes(user)
  const down = user.downvotes || 0
  const total = up + down
  return total === 0 ? null : up / total // null = neutral/no votes yet
}

export function getVoteColor (user) {
  const ratio = getVoteRatio(user)
  if (ratio === null) return '#c5c8ce'
  const lerp = (a, b) => Math.round(a + (b - a) * ratio)
  return `rgb(${lerp(0x19, 0xed)}, ${lerp(0xbe, 0x40)}, ${lerp(0x6b, 0x14)})` // green -> red
}

export function getVoteFill (user, n = VOTE_VOLUME_N) {
  const up = getEffectiveUpvotes(user)
  const down = user.downvotes || 0
  return Math.min((up + down) / n, 1)
}
