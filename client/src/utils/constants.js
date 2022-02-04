export const JUDGE_STATUS = {
  '-2': {
    name: 'Compile Error',
    short: 'CE',
    color: 'warning',
    type: 'warning'
  },
  '-1': {
    name: 'Wrong Answer',
    short: 'WA',
    color: 'error',
    type: 'error'
  },
  '0': {
    name: 'Accepted',
    short: 'AC',
    color: 'success',
    type: 'success'
  },
  '1': {
    name: 'Time Limit Exceeded',
    short: 'TLE',
    color: 'error',
    type: 'error'
  },
  '2': {
    name: 'Time Limit Exceeded',
    short: 'TLE',
    color: 'error',
    type: 'error'
  },
  '3': {
    name: 'Memory Limit Exceeded',
    short: 'MLE',
    color: 'error',
    type: 'error'
  },
  '4': {
    name: 'Runtime Error',
    short: 'RE',
    color: 'error',
    type: 'error'
  },
  '5': {
    name: 'System Error',
    short: 'SE',
    color: 'error',
    type: 'error'
  },
  '6': {
    name: 'Pending',
    color: 'warning',
    type: 'warning'
  },
  '7': {
    name: 'Judging',
    color: 'primary',
    type: 'info'
  },
  '8': {
    name: 'Partial Accepted',
    short: 'PAC',
    color: 'primary',
    type: 'info'
  },
  '9': {
    name: 'Submitting',
    color: 'warning',
    type: 'warning'
  }
}

export const CONTEST_STATUS = {
  'NOT_START': '1',
  'UNDERWAY': '0',
  'ENDED': '-1'
}

export const CONTEST_STATUS_REVERSE = {
  '1': {
    name: 'Not Started',
    color: 'warning'
  },
  '0': {
    name: 'Underway',
    color: 'success'
  },
  '-1': {
    name: 'Ended',
    color: 'error'
  }
}

export const CONTEST_TYPE = {
  PUBLIC: 'Public',
  PRIVATE: 'Password Protected'
}

export const CONTEST_DIVISIONS = [
  'Advanced',
  'Intermediate',
  'Novice'
]

export const USER_TYPE = {
  REGULAR_USER: 'Regular User',
  ADMIN: 'Admin',
  SUPER_ADMIN: 'Super Admin',
  TESTER: 'Tester'
}

export const PROBLEM_PERMISSION = {
  NONE: 'None',
  OWN: 'Own',
  ALL: 'All'
}

export const STORAGE_KEY = {
  AUTHED: 'authed',
  PROBLEM_CODE: 'problemCode',
  languages: 'languages'
}

export function buildProblemCodeKey (problemID, contestID = null) {
  if (contestID) {
    return `${STORAGE_KEY.PROBLEM_CODE}_${contestID}_${problemID}`
  }
  return `${STORAGE_KEY.PROBLEM_CODE}_NaN_${problemID}`
}
