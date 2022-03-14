<template>
  <div class="home">
    <!-- 配信者を選択するエリア -->
    <ChStreamerForm />
  </div>
</template>

<script>
import ChStreamerForm from '@/components/molecules/ChStreamerForm.vue'

export default {
  name: 'Home',
  components: {
    ChStreamerForm
  }
}
</script>
