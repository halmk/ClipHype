<template>
  <ChHeader />
  <ChSideBar />
  <router-view/>
  <ChFooter />
</template>

<script>
import ChHeader from '@/components/molecules/ChHeader.vue'
import ChSideBar from '@/components/molecules/ChSideBar.vue'
import ChFooter from '@/components/molecules/ChFooter.vue'

export default {
  components: {
    ChHeader,
    ChSideBar,
    ChFooter
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  background-color: #f8f9fa;
}

html {
  background-color: #f8f9fa;
}
</style>
