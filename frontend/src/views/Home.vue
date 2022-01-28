<template>
  <div class="home">
    <!-- ページのヘッダ -->
    <ChNavigationBar />
    <!-- 現在のステップを表すサイドバー -->
    <ChSideBar />
    <!-- 配信者を選択するエリア -->
    <ChStreamerForm />
  </div>
</template>

<script>
// @ is an alias to /src
import ChNavigationBar from '@/components/molecules/ChNavigationBar.vue'
import ChSideBar from '@/components/molecules/ChSideBar.vue'
import ChStreamerForm from '@/components/molecules/ChStreamerForm.vue'


export default {
  name: 'Home',
  components: {
    ChNavigationBar,
    ChSideBar,
    ChStreamerForm
  }
}
</script>
