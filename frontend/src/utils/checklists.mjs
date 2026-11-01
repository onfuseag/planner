// Categories are text on each checklist point, not separate documents.
const categoryOf = (row) => row.category || ''

export function groupChecklistRows(rows) {
  const groups = new Map()

  for (const row of rows) {
    const category = categoryOf(row)
    if (!groups.has(category)) {
      groups.set(category, { category, rows: [] })
    }
    groups.get(category).rows.push(row)
  }

  return Array.from(groups.values())
}

export function addChecklistRow(rows, category) {
  const row = {
    doctype: 'Project Checklist Point',
    category: category || '',
    task: '',
    data: '',
    status: 'Open',
    image: '',
  }

  let insertionIndex = rows.length
  for (let index = rows.length - 1; index >= 0; index--) {
    if (categoryOf(rows[index]) === row.category) {
      insertionIndex = index + 1
      break
    }
  }
  rows.splice(insertionIndex, 0, row)
  return row
}

export function renameChecklistCategory(rows, from, to) {
  const oldCategory = from || ''
  const newCategory = to || ''

  for (const row of rows) {
    if (categoryOf(row) === oldCategory) {
      row.category = newCategory
    }
  }
  return rows
}

export function prepareChecklistForSave(document) {
  // Keep modified so Frappe can reject stale edits, and persist the visible row order.
  const copy = JSON.parse(JSON.stringify(document))
  if (Array.isArray(copy.checklist)) {
    copy.checklist.forEach((row, index) => {
      row.idx = index + 1
    })
  }
  return copy
}

export function createChecklistFromTemplate(template, { date, project } = {}) {
  if (template?.status !== 'Template') {
    throw new Error(
      'Only checklists with status Template can be used as a template.',
    )
  }

  // Copy content only: Frappe assigns new document identities on insertion.
  return {
    doctype: 'Project Checklist',
    type: template.type || '',
    project: project ?? template.project ?? '',
    date,
    status: 'Open',
    pretext: template.pretext ?? '',
    posttext: template.posttext ?? '',
    customer: template.customer ?? '',
    customer_mail: template.customer_mail ?? '',
    position: template.position ?? '',
    user: template.user ?? '',
    checklist: (template.checklist || []).map((row, index) => ({
      doctype: 'Project Checklist Point',
      category: row.category ?? '',
      task: row.task ?? '',
      data: row.data ?? '',
      status: row.status ?? '',
      image: row.image ?? '',
      idx: index + 1,
    })),
  }
}
