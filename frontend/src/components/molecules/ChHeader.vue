<template>
  <div class="chheader">
    <nav class="navbar navbar-expand navbar-white bg-white navbar-clip shadow-sm">
      <div class="container">
        <div class="mr-1 rounded">
          <!-- ClipHype Logo Atom -->
          <ChLogo />
        </div>
        <!-- NavBar -->
        <ChNavigationBar />
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbar-content">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbar-content">
          <ul class="navbar-nav">
            <li class="navbar-item">
              <a href="{% url 'account_login' %}" class="btn btn-primary">Login</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'ChHeader'
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
