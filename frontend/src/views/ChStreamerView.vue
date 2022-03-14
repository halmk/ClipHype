<template>
  <div class="streamer bg-white m-1 p-2 shadow">
    <h1>Streamer View Here !!!</h1>
    <h2>Streamer name is {{ $route.params.id }}</h2>
    <h2>{{ $route.fullPath }}</h2>
    <div class="row">
      <div class="col-3">
        <router-link :to="'/streamer/'+ $route.params.id +'/archives'">
        <button class="btn btn-primary">
          Archives
        </button>
        </router-link>
      </div>
      <div class="col-3">
        <router-link :to="'/streamer/' + $route.params.id + '/clips'">
          <button class="btn btn-primary">
            Clips
          </button>
        </router-link>
      </div>
      <div class="col-3">
        <router-link :to="'/streamer/' + $route.params.id + '/highlights'">
          <button class="btn btn-primary">
            Highlights
          </button>
        </router-link>
      </div>
      <div class="col-3">
        <router-link :to="'/streamer/' + $route.params.id + '/videos'">
          <button class="btn btn-primary">
            Videos
          </button>
        </router-link>
      </div>
    </div>
    <div class="mt-3">
      <router-view></router-view>
    </div>
  </div>
</template>
