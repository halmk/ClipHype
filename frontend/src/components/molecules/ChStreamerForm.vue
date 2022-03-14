<template>
  <div class="container streamer-form">
    <h1>Streamer Form Here !!!</h1>
    <div class="mt-2 mb-3">
      <ChStreamerSearch />
    </div>
    <div class="mt-2">
      <ChStreamerList />
    </div>
  </div>
</template>

<script>
import ChStreamerSearch from '@/components/molecules/ChStreamerSearch.vue'
import ChStreamerList from '@/components/molecules/ChStreamerList.vue'

export default {
  name: 'ChStreamerForm',
  components: {
    ChStreamerSearch,
    ChStreamerList
  }
}
</script>

<style scoped>
</style>
