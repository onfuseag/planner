import { toast } from 'frappe-ui'
import { ref } from 'vue'

export { default as dayjs } from './dayjs'

export const raiseToast = (type, message) => {
  if (type === 'success')
    return toast({
      title: 'Success',
      text: message,
      icon: 'check-circle',
      position: 'bottom-right',
      iconClasses: 'text-green-500',
    })

  const div = document.createElement('div')
  div.innerHTML = message
  // strip html tags
  const text =
    div.textContent ||
    div.innerText ||
    'Failed to perform action. Please try again later.'
  toast({
    title: 'Error',
    text: text,
    icon: 'alert-circle',
    position: 'bottom-right',
    iconClasses: 'text-red-500',
    timeout: 7,
  })
}

export const goTo = (path) => {
  window.location.href = path
}
export const goToBlank = (path) => {
  window.open(path, '_blank')
}

export const dateFormat = ref('YYYY-MM-DD')

export function fuzzySearch(arr, { term, keys }) {
  // search for term in all keys of arr items and sort by relevance
  const lowerCaseTerm = term.toLowerCase()
  const results = arr.reduce((acc, item) => {
    const score = keys.reduce((acc, key) => {
      const value = item[key]
      if (value) {
        const match = value.toLowerCase().indexOf(lowerCaseTerm)
        if (match !== -1) {
          return acc + match + 1
        }
      }
      return acc
    }, 0)
    if (score) {
      acc.push({ item, score })
    }
    return acc
  }, [])
  return results.sort((a, b) => a.score - b.score).map((item) => item.item)
}
