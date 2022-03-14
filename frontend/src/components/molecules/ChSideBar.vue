<template>
  <div class="sidebar">
    <nav class="navbar navbar-expand navbar-white bg-light navbar-clip shadow-sm">
      <span>
        <router-link to="/">
        Select Streamer
        </router-link>
      </span>
      <span class="ml-1">></span>
      <span class="ml-1">
        <router-link to="archives">
        Choose Archive
        </router-link>
      </span>
      <span class="ml-1">></span>
      <span class="ml-1">
        <router-link to="clips">
        Choose Clips
        </router-link>
      </span>
      <span class="ml-1">></span>
      <span class="ml-1">
        <router-link to="highlights">
        Create Highlights Video
        </router-link>
      </span>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'ChSideBar.vue'
}
</script>

<style scoped>
</style>
