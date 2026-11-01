import assert from 'node:assert/strict'
import test from 'node:test'
import {
  addChecklistRow,
  createChecklistFromTemplate,
  groupChecklistRows,
  prepareChecklistForSave,
  renameChecklistCategory,
} from './checklists.mjs'

test('interleaved points are grouped in first-seen order without changing saved order', () => {
  const rows = Object.freeze([
    Object.freeze({ name: 'a', category: 'Safety', task: 'Check switch' }),
    Object.freeze({
      name: 'b',
      category: 'Electrical',
      task: 'Measure voltage',
    }),
    Object.freeze({ name: 'c', category: 'Safety', task: 'Check guard' }),
  ])

  const groups = groupChecklistRows(rows)

  assert.deepEqual(
    groups.map((group) => group.category),
    ['Safety', 'Electrical'],
  )
  assert.deepEqual(
    groups[0].rows.map((row) => row.name),
    ['a', 'c'],
  )
  assert.equal(groups[0].rows[0], rows[0])
  assert.equal(groups[0].rows[1], rows[2])
  assert.equal(groups[1].rows[0], rows[1])
  assert.deepEqual(
    rows.map((row) => row.name),
    ['a', 'b', 'c'],
  )
})

test('missing category text is grouped together while meaningful text stays exact', () => {
  const rows = [
    { category: null },
    {},
    { category: '' },
    { category: 'Safety ' },
    { category: 'Safety' },
  ]

  const groups = groupChecklistRows(rows)

  assert.deepEqual(
    groups.map((group) => group.category),
    ['', 'Safety ', 'Safety'],
  )
  assert.deepEqual(groups[0].rows, rows.slice(0, 3))
  assert.equal(rows[0].category, null)
  assert.equal(Object.hasOwn(rows[1], 'category'), false)
  assert.deepEqual(groupChecklistRows([]), [])
})

test('category names are safe as plain text even when they resemble object properties', () => {
  const rows = [
    { category: '__proto__', task: 'One' },
    { category: 'constructor', task: 'Two' },
    { category: '__proto__', task: 'Three' },
    { category: '<script>alert(1)</script>', task: 'Four' },
  ]

  const groups = groupChecklistRows(rows)

  assert.deepEqual(
    groups.map((group) => group.category),
    ['__proto__', 'constructor', '<script>alert(1)</script>'],
  )
  assert.equal(groups[0].rows.length, 2)
})

test('adding a line inherits the category and inserts after its last existing point', () => {
  const rows = [
    { name: 'a', category: 'Safety' },
    { name: 'b', category: 'Electrical' },
    { name: 'c', category: 'Safety' },
    { name: 'd', category: 'Handover' },
  ]

  const added = addChecklistRow(rows, 'Safety')

  assert.deepEqual(added, {
    doctype: 'Project Checklist Point',
    category: 'Safety',
    task: '',
    data: '',
    status: 'Open',
    image: '',
  })
  assert.equal(rows[3], added)
  assert.deepEqual(
    rows.filter((row) => row.name).map((row) => row.name),
    ['a', 'b', 'c', 'd'],
  )
})

test('new categories append and uncategorized additions join missing category rows', () => {
  const rows = [{ category: null }, { category: 'Safety' }]
  const uncategorized = addChecklistRow(rows)
  assert.equal(uncategorized.category, '')
  assert.equal(rows[1], uncategorized)

  const newCategory = addChecklistRow(rows, 'Handover')
  assert.equal(rows.at(-1), newCategory)
  assert.equal(newCategory.category, 'Handover')
})

test('renaming can merge groups without changing point identity or PDF fields', () => {
  const rows = [
    {
      name: 'a',
      category: 'Safety',
      task: 'Guard',
      status: 'Not applicable',
      data: '',
      image: '/private/files/a.jpg',
      idx: 1,
    },
    {
      name: 'b',
      category: 'Electrical',
      task: 'Voltage',
      status: 'Data',
      data: '230 V',
      image: '',
      idx: 2,
    },
    {
      name: 'c',
      category: 'Safety',
      task: 'Switch',
      status: 'Done',
      data: 'Checked',
      image: '/files/c.jpg',
      idx: 3,
    },
  ]
  const originalRows = [...rows]
  const originalFields = rows.map(({ category, ...fields }) => fields)

  renameChecklistCategory(rows, 'Safety', 'Electrical')

  assert.equal(groupChecklistRows(rows).length, 1)
  for (let index = 0; index < rows.length; index++) {
    assert.equal(rows[index], originalRows[index])
    const { category, ...fields } = rows[index]
    assert.equal(category, 'Electrical')
    assert.deepEqual(fields, originalFields[index])
  }
})

test('renaming supports both directions between named and uncategorized points', () => {
  const rows = [{ category: null }, {}, { category: '' }, { category: 'Other' }]

  renameChecklistCategory(rows, '', 'Safety')
  assert.deepEqual(
    rows.map((row) => row.category),
    ['Safety', 'Safety', 'Safety', 'Other'],
  )

  renameChecklistCategory(rows, 'Safety', '')
  assert.deepEqual(
    rows.map((row) => row.category),
    ['', '', '', 'Other'],
  )
})

test('save preparation persists edited row order without losing records or mutating the draft', () => {
  const document = {
    doctype: 'Project Checklist',
    name: 'checklist-123',
    modified: '2026-11-01 12:34:56.123456',
    project: 'PROJECT-1',
    type: 'Inspection',
    status: 'Open',
    posttext: 'Customer signature follows',
    custom_report_settings: { include_images: true },
    checklist: [
      {
        name: 'point-1',
        category: 'Safety',
        task: 'Guard',
        status: 'Not applicable',
        data: '',
        image: '/private/files/a.jpg',
        idx: 4,
      },
      {
        name: 'point-2',
        category: 'Electrical',
        task: 'Voltage',
        status: 'Data',
        data: '230 V',
        image: '/files/b.jpg',
        idx: 2,
      },
      {
        name: 'point-3',
        category: 'Safety',
        task: 'Switch',
        status: 'Done',
        data: 'Checked',
        image: '',
        idx: 6,
      },
    ],
  }
  const added = addChecklistRow(document.checklist, 'Safety')
  Object.assign(added, {
    task: 'Warning label',
    data: 'Visible',
    image: '/files/new.jpg',
  })
  const original = JSON.parse(JSON.stringify(document))

  const saved = prepareChecklistForSave(document)

  assert.notEqual(saved, document)
  assert.equal(saved.name, 'checklist-123')
  assert.equal(saved.modified, '2026-11-01 12:34:56.123456')
  assert.equal(saved.posttext, original.posttext)
  assert.deepEqual(
    saved.custom_report_settings,
    original.custom_report_settings,
  )
  assert.deepEqual(
    saved.checklist.map((row) => row.name),
    ['point-1', 'point-2', 'point-3', undefined],
  )
  assert.deepEqual(
    saved.checklist.map((row) => row.idx),
    [1, 2, 3, 4],
  )
  assert.equal(saved.checklist.length, original.checklist.length)
  for (let index = 0; index < saved.checklist.length; index++) {
    const { idx: savedIndex, ...savedFields } = saved.checklist[index]
    const { idx: draftIndex, ...draftFields } = original.checklist[index]
    assert.deepEqual(savedFields, draftFields)
    assert.notEqual(saved.checklist[index], document.checklist[index])
  }
  assert.deepEqual(document, original)

  saved.checklist[0].task = 'Changed only in saved copy'
  saved.custom_report_settings.include_images = false
  assert.deepEqual(document, original)
})

test('templates become new open checklists with content and fresh row indexes only', () => {
  const lifecycle = {
    name: 'template-123',
    parent: 'old-parent',
    parenttype: 'Project Checklist',
    parentfield: 'checklist',
    owner: 'template-owner@example.com',
    creation: '2024-01-01 00:00:00',
    modified: '2026-11-01 12:34:56.123456',
    __islocal: 0,
    docstatus: 0,
  }
  const template = {
    ...lifecycle,
    doctype: 'Project Checklist',
    status: 'Template',
    type: 'Inspection',
    project: 'PROJECT-TEMPLATE',
    project_name: 'Fetched project title',
    date: '2024-01-01',
    pretext: 'Check the installation',
    posttext: 'Signature follows',
    customer: 'Customer name',
    customer_mail: 'customer@example.com',
    position: 'Site manager',
    user: 'contact@example.com',
    user_name: 'Fetched user name',
    custom_field: 'Not copied',
    checklist: [
      {
        ...lifecycle,
        name: 'template-point-data',
        doctype: 'Project Checklist Point',
        category: 'Measurements',
        task: 'Voltage',
        data: '230 V',
        status: 'Data',
        image: '/private/files/measurement.jpg',
        idx: 9,
        custom_field: 'Not copied',
      },
      {
        ...lifecycle,
        name: 'template-point-na',
        doctype: 'Project Checklist Point',
        category: 'Optional checks',
        task: 'Roof access',
        data: '',
        status: 'Not applicable',
        image: '/files/access.jpg',
        idx: 4,
      },
    ],
  }
  const original = JSON.parse(JSON.stringify(template))

  const draft = createChecklistFromTemplate(template, { date: '2026-11-02' })

  assert.notEqual(draft, template)
  assert.deepEqual(draft, {
    doctype: 'Project Checklist',
    type: 'Inspection',
    project: 'PROJECT-TEMPLATE',
    date: '2026-11-02',
    status: 'Open',
    pretext: 'Check the installation',
    posttext: 'Signature follows',
    customer: 'Customer name',
    customer_mail: 'customer@example.com',
    position: 'Site manager',
    user: 'contact@example.com',
    checklist: [
      {
        doctype: 'Project Checklist Point',
        category: 'Measurements',
        task: 'Voltage',
        data: '230 V',
        status: 'Data',
        image: '/private/files/measurement.jpg',
        idx: 1,
      },
      {
        doctype: 'Project Checklist Point',
        category: 'Optional checks',
        task: 'Roof access',
        data: '',
        status: 'Not applicable',
        image: '/files/access.jpg',
        idx: 2,
      },
    ],
  })
  assert.notEqual(draft.checklist, template.checklist)
  for (let index = 0; index < draft.checklist.length; index++) {
    assert.notEqual(draft.checklist[index], template.checklist[index])
  }
  assert.deepEqual(template, original)

  draft.checklist[0].data = '240 V'
  draft.checklist[1].status = 'Open'
  draft.checklist.push({ task: 'New point' })
  draft.customer = 'Another customer'
  assert.deepEqual(template, original)
})

test('template project can be inherited, replaced, or intentionally cleared', () => {
  const template = { status: 'Template', project: 'PROJECT-TEMPLATE' }

  assert.equal(
    createChecklistFromTemplate(template).project,
    'PROJECT-TEMPLATE',
  )
  assert.equal(
    createChecklistFromTemplate(template, { project: 'PROJECT-NEW' }).project,
    'PROJECT-NEW',
  )
  assert.equal(
    createChecklistFromTemplate(template, { project: '' }).project,
    '',
  )
  assert.equal(createChecklistFromTemplate({ status: 'Template' }).project, '')
})

test('template defaults preserve empty status and provide missing text fields without inventing dates', () => {
  const draft = createChecklistFromTemplate({
    status: 'Template',
    checklist: [{ task: 'Check switch', status: '' }],
  })

  assert.equal(draft.type, '')
  assert.equal(draft.date, undefined)
  assert.equal(draft.status, 'Open')
  assert.equal(draft.pretext, '')
  assert.equal(draft.posttext, '')
  assert.equal(draft.user, '')
  assert.deepEqual(draft.checklist, [
    {
      doctype: 'Project Checklist Point',
      category: '',
      task: 'Check switch',
      data: '',
      status: '',
      image: '',
      idx: 1,
    },
  ])
})

test('ordinary checklists cannot be used as templates', () => {
  for (const template of [
    undefined,
    null,
    {},
    { status: 'Open' },
    { status: 'Completed' },
  ]) {
    assert.throws(
      () => createChecklistFromTemplate(template),
      /Only checklists with status Template/,
    )
  }
})
