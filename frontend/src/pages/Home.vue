<template>
  <div>
    <h1>Planner</h1>
    <div class="p-2">
      <TextInput
        :type="'text'"
        size="lg"
        variant="outline"
        placeholder="Suche ..."
        :disabled="false"
        modelValue=""
      />
    </div>
  </div>
  

  <div class="wrapper">
    <div v-for="airport in airports" :key="airport.abbreviation" class="airport">
      <p>{{ airport.abbreviation }}</p>
      <p>{{ airport.name }}</p>
      <p>{{ airport.city }}, {{ airport.state }}</p>
    </div>
  </div>
  <ul>
    <li v-for="user in users.data">{{ user.name }} {{ user.full_name }}</li>
    <Avatar
      :shape="'circle'"
      :image="null"
      label="EY"
      size="md"
    />
  </ul>

  <g-gantt-chart
    chart-start="2024-02-12 12:00"
    chart-end="2024-02-18 12:00"
    precision="day"
    bar-start="myBeginDate"
    bar-end="myEndDate"
    color-scheme="sky"
  >
    <g-gantt-row label='<h2>oiii</h2>' :bars="row1BarList" />
    <g-gantt-row label="My row 2" :bars="row2BarList" />
  </g-gantt-chart>
</template>

<script setup>
import { Dialog, Avatar, TextInput, createListResource } from 'frappe-ui'
import { ref } from "vue"

  const row1BarList = ref([
    {
      myBeginDate: "2024-02-13 13:00",
      myEndDate: "2024-02-13 19:00",
      ganttBarConfig: {
        // each bar must have a nested ganttBarConfig object ...
        id: "unique-id-1", // ... and a unique "id" property
        label: "Lorem ipsum dolor",
        immobile: true,
      }
    }
  ])
  const row2BarList = ref([
    {
      myBeginDate: "2024-02-13 00:00",
      myEndDate: "2024-02-14 02:00",
      ganttBarConfig: {
        id: "another-unique-id-2",
        hasHandles: true,
        label: "Hey, look at me",
        style: {
          // arbitrary CSS styling for your bar
          background: "#e09b69",
          borderRadius: "20px",
          color: "black",
          
        },
        immobile: true,
        class: "foo" // you can also add CSS classes to your bars!
      },
    }
  ])

let users = createListResource({
  doctype: 'User',
  fields: ["name","full_name"],
  auto: true,
})

console.log(users)
</script>
