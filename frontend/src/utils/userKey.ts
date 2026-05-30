export function getUserKey(): string {
  let key = localStorage.getItem('user_key')
  if (!key) {
    key = crypto.randomUUID()
    localStorage.setItem('user_key', key)
  }
  return key
}
