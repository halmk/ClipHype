<template>
  <div class="streamer-search">
    <div class="mt-5">
      <input type="text" placeholder="kato_junichi0817" v-model="streamerName" class="input-lg border rounded shadow-sm pl-2 py-1" required>
      <button class="btn btn-outline-primary ml-2 px-2 shadow-sm" v-on:click="getStreamerId">
        GO
      </button>
    </div>
  </div>
</template>

<script>

export default {
}
</script>
