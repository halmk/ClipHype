Vue.component('paginate', VuejsPaginate);
Vue.component('datepicker', vuejsDatepicker);

const csrftoken = Cookies.get('csrftoken');

AWS.config.region = 'ap-northeast-1'; // リージョン
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'ap-northeast-1:9df84405-ad0f-4573-a202-3f5627cb64c9',
});
var s3 = new AWS.S3({
  apiVersion: '2006-03-01',
  params: {Bucket: bucket_name}
});


var app = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],

  data: {
    siteUrl: '',
    clientId: '',
    follows: [],
    userIds: [],
    followsLength: 0,
    followsParPage: 6,
    followsCurrentPage: 1,
    clips: [],
    publishedClips: [],
    clipsParPage: 6,
    clipsCurrentPage: 1,
    token: '',
    datepickerStartedAt: '2019-01-01',
    datepickerEndedAt: '2019-09-03',
    DatePickerFormat: 'yyyy-MM-dd',
    published: false,
    clipsAfter: '',
    username: '',
    streamerName: '',
    streamerId: '',
    videos: [],
    videosParPage: 2,
    videosCurrentPage: 1,
    width: window.innerWidth,
    archiveStartDate: '',
    archiveEndDate: '',
    clipEmbedUrl: '',
    timelineClips: [],
    timelineParPage: 4,
    timelinePageIndex: 0,
    timelineEmbedUrl: '',
    totalClipSeconds: 0,
    playTimeExceeded: false,
    highlights: [],
    digestUrl: '',
    taskId: '',
    title: '',
    transition: 'fade',
    duration: 500,
    disabledCreateButton: true,
    isDrawText: false,
    fontsize: 64,
    fontcolor: "white",
    borderw: 1,
    position: "top-left",
    isFLTransition: false,
  },

  computed: {
    /* ページング内で表示するクリップを返す */
    getFollowsItems: function() {
      let current = this.followsCurrentPage * this.followsParPage;
      let start = current - this.followsParPage;
      return this.follows.slice(start, current);
    },

    /* ページングのページ数を返す */
    getFollowsPageCount: function() {
      return Math.ceil(this.follows.length / this.followsParPage);
    },

    /* ページング内で表示するクリップを返す */
    getClipsItems: function() {
      let current = this.clipsCurrentPage * this.clipsParPage;
      let start = current - this.clipsParPage;
      if(this.published) return this.publishedClips.slice(start, current);
      else return this.clips.slice(start, current);
    },

    /* ページングのページ数を返す */
    getClipsPageCount: function() {
      if(this.published) return Math.ceil(this.publishedClips.length / this.clipsParPage);
      else return Math.ceil(this.clips.length / this.clipsParPage);
    },

    /* ページング内で表示するクリップを返す */
    getVideosItems: function() {
      let current = this.videosCurrentPage * this.videosParPage;
      let start = current - this.videosParPage;
      return this.videos.slice(start, current);
    },
    /* ページングのページ数を返す */
    getVideosPageCount: function() {
      return Math.ceil(this.videos.length / this.videosParPage);
    },

    getTimelineItems: function () {
      beginIndex = this.timelinePageIndex;
      endIndex = this.timelinePageIndex + this.timelineParPage;
      return this.timelineClips.slice(beginIndex,endIndex);
    },

    getTimelineClipsId: function () {
      let clips_id = [];
      clips_id.push(this.streamerName);
      for(let i=0; i<this.timelineClips.length; i++){
        clips_id.push(this.timelineClips[i]['id']);
      }
      return clips_id;
    },

    getTotalClipSeconds: function() {
      let playtime = this.totalClipSeconds;
      let min = ('00' + Math.floor(playtime / 60)).slice(-2);
      let sec = ('00' + playtime % 60).slice(-2);
      return `${min}m ${sec}s`;
    },

    getHighlightsItems: function() {
      let start = 0;
      let end = this.highlights.length;
      return this.highlights.slice(start,end);
    }
  },

  watch: {
    /* 指定日時が変化したらクリップを読み込む */
    datepickerStartedAt: function() {
      if (this.streamerId.length != 0) this.getClips();
    },
    datepickerEndedAt: function() {
      if (this.streamerId.length != 0) this.getClips();
    },

    clientId: function() {
      this.getFollows();
    },

    /* 配信者のIDが変化したらクリップとアーカイブを読み込む */
    streamerId: function() {
      this.getClips();
      this.getVideos();
    },

    /* published が true になったとき、getPublishedClips() を呼び出す */
    published: function() {
      if(this.published) this.getPublishedClips();
    },

    width: function() {
      this.setResponsiveItems();
    },

    duration: function() {
      this.duration = Number(this.duration);
      if(this.duration > 2000) this.duration = 2000;
      if(this.duration < 200) this.duration = 200;
    },

    totalClipSeconds: function() {
      if(this.totalClipSeconds > 300) {
        this.playTimeExceeded = true;
        this.disabledCreateButton = true;
      }
      else {
        this.playTimeExceeded = false;
        this.disabledCreateButton = false;
      }
      if(this.timelineClips.length <= 1) this.disabledCreateButton = true;
    },
  },

  methods: {
    /* ページネーションをクリックしたとき、ページ番号を更新 */
    clickClipsCallback: function(pageNum) {
      this.clipsCurrentPage = Number(pageNum);
    },

    /* ページネーションをクリックしたとき、ページ番号を更新 */
    clickFollowsCallback: function(pageNum) {
      this.followsCurrentPage = Number(pageNum);
    },

    /* ページネーションをクリックしたとき、ページ番号を更新 */
    clickClipsCallback: function(pageNum) {
      this.clipsCurrentPage = Number(pageNum);
    },

    /* 文字列を'YYYY-MM-DD'に変換したものを返す */
    customformat: function(value) {
      return moment(value).format('YYYY-MM-DD');
    },

    getEpochTime: function(dt) {
      return moment(dt).unix();
    },

    /*
       ----------------------
        Twitch API Requests
       ----------------------
    */

    /* ストリーマの名前からストリーマIDを取得する */
    getStreamerId: function() {
      TwitchAPI.getUserId(this.streamerName)
        .then(function (response) {
          app.streamerId = response['data']['data'][0]['id'];
        })
        .catch(function (error) {
          console.log(error);
        })
    },

    getClientId: function() {
      TwitchAPI.getUserId(this.userName)
        .then(function (response) {
          app.clientId = response['data']['data'][0]['id'];
        })
        .catch(function (error) {
          console.log(error);
        })
    },

    /* ユーザがフォローしているユーザの情報を取得する */
    getFollows: function() {
      TwitchAPI.getFollows(this.clientId)
        .then(function(response) {
          //console.log("getUsersFollows↓");
          //console.log(response);
          app.follows = response['data']['data'];
          app.userIds = [];
          for(let i=0; i<app.follows.length; i++){
            app.userIds.push(app.follows[i]['to_id']);
          }
          app.getUsers();
        })
        .catch(function(error) {
          //console.log(error.response);
        })
    },


    /* ユーザがフォローしているユーザのプロフィール画像とログインIDを取得する */
    getUsers: function() {
      TwitchAPI.getUsers(this.userIds)
        .then(function(response) {
          //console.log("getUsers↓");
          //console.log(response);
          let data = response['data']['data'];
          for(let i=0; i<data.length; i++){
            for(let j=0; j<app.follows.length; j++){
              if(data[i]['id'] == app.follows[j]['to_id']) {
                if(response['data']['data'][i]['profile_image_url'] === ""){
                  app.$set(app.follows[j], "profile_image_url", 'https://static-cdn.jtvnw.net/jtv_user_pictures/xarth/404_user_70x70.png');
                } else {
                  app.$set(app.follows[j], "profile_image_url", response['data']['data'][i]['profile_image_url']);
                }
              }
            }
          }
        })
        .catch(function(error) {
          //console.log(error.response);
        })
    },


    /* 配信者のIDを指定して、その配信のクリップを取得する */
    getClips: function() {
      TwitchAPI.getClips(this.streamerId, this.datepickerStartedAt, this.datepickerEndedAt)
        .then(function (response) {
          //console.log("getClips↓:成功");
          console.log(response);
          app.clips = response['data']['data'];
          for(let i=0; i<response['data']['data'].length; i++){
            app.clips[i]['modal_id'] = 'modal' + app.clips[i]['id'];
            app.clips[i]['modal_target'] = '#' + app.clips[i]['modal_id'];
            app.clips[i]['embed_url'] += `&autoplay=false&parent=${app.siteUrl}`;
            app.clips[i]['modal'] = false;
            app.clips[i]['created_date'] = app.customformat(app.clips[i]['created_at']);
            app.clips[i]['created_epoch'] = app.getEpochTime(app.clips[i]['created_at']);
          }
          app.clipsAfter = response['data']['pagination']['cursor'];
          if(app.published) app.getPublishedClips();
        })
        .catch(function (error) {
          //console.log("getClips:失敗");
          console.log(error);
        })
    },

    /* クリップのIDを指定してクリップを取得する */
    getClipById: function(clip_id, index) {
      TwitchAPI.getClipById(clip_id)
        .then(function (response) {
          //console.log("getClipById↓:成功");
          //console.log(response);
          response['data']['data'][0]['isHover'] = false;
          response['data']['data'][0]['index'] = index;
          app.timelineClips.push(response['data']['data'][0]);
          app.addClipPlayTime(response['data']['data'][0]['thumbnail_url']);
          app.timelineClips.sort(app.timelineCmp);
        })
        .catch(function (error) {
          //console.log("getClipById:失敗");
          //console.log(error);
          //console.log(error.response);
        })
    },

    /* afterで指定されているクリップデータを追加で読み込む */
    getAfterClips: function() {
      //console.log("after : " + this.clipsAfter);
      if(!this.clipsAfter){
        alert("No more clips!");
        return;
      }
      TwitchAPI.getAfterClips(this.streamerId, this.datepickerStartedAt, this.datepickerEndedAt, this.clipsAfter)
        .then(function (response) {
          //console.log("getAfterClips↓:成功");
          //console.log(response);
          let data = response['data']['data'];

          for(let i=0; i<response['data']['data'].length; i++){
            data[i]['modal_id'] = 'modal' + data[i]['id'];
            data[i]['modal_target'] = '#' + data[i]['modal_id'];
            data[i]['embed_url'] += `&autoplay=false&parent=${this.siteUrl}`;
            data[i]['modal'] = false;
            data[i]['created_at'] = app.customformat(data[i]['created_at']);
          }
          //Array.prototype.push.apply(app.clips, data);
          for(let i=0; i<data.length; i++){
            app.clips.push(data[i]);
          }
          app.clipsAfter = response['data']['pagination']['cursor'];
          if(app.published) app.getPublishedClips();
        })
        .catch(function (error) {
          //console.log("getAfterClips:失敗");
          //console.log(error.response);
        })
    },

    /* 配信アーカイブを取得する */
    getVideos: function() {
      TwitchAPI.getVideos(this.streamerId)
        .then(function(response) {
          //console.log("getVideos↓");
          console.log(response);
          app.videos = response['data']['data'];
          for(let i=0; i<response['data']['data'].length; i++){
            let thumbnailUrl = app.videos[i]['thumbnail_url'];
            if(thumbnailUrl === ""){
              app.videos[i]['thumbnail_url'] = "https://vod-secure.twitch.tv/_404/404_processing_320x180.png";
            } else {
              app.videos[i]['thumbnail_url'] = thumbnailUrl.replace('-%{width}x%{height}', '-320x180');
            }
            app.videos[i]['date'] = app.customformat(app.videos[i]['created_at']);
          }
        })
        .catch(function(error) {
          console.log(error);
        })
    },

    /* 配信者のIDを指定して、その配信のクリップを取得する */
    getArchiveClips: function() {
      this.clipsCurrrentPage = 1;

      TwitchAPI.getArchiveClips(this.streamerId, this.archiveStartDate, this.archiveEndDate)
        .then(function (response) {
          //console.log("getArchiveClips↓:成功");
          //console.log(response);
          app.clips = response['data']['data'];
          for(let i=0; i<response['data']['data'].length; i++){
            app.clips[i]['modal_id'] = 'modal' + app.clips[i]['id'];
            app.clips[i]['modal_target'] = '#' + app.clips[i]['modal_id'];
            app.clips[i]['embed_url'] += `&autoplay=false&parent=${app.siteUrl}`;
            app.clips[i]['modal'] = false;
            app.clips[i]['created_at'] = app.customformat(app.clips[i]['created_at']);
          }
          app.clipsAfter = response['data']['pagination']['cursor'];
          if(app.published) app.getPublishedClips();
        })
        .catch(function (error) {
          //console.log("getClips:失敗");
          //console.log(error.response);
        })
    },

    /*
        ---------------------------------
    */

    /* 現在Clipsにあるクリップからタイトルが設定されたものだけに絞り込む */
    getPublishedClips: function() {
      let publishedClips = [];
      for(let i=0; i<this.clips.length; i++){
        let isPublished = true;
        for(let j=0; j<this.videos.length; j++){
          if(this.clips[i]['title'] === this.videos[j]['title']){
            isPublished = false;
            break;
          }
        }
        if(isPublished){
          publishedClips.push(this.clips[i]);
        }
      }
      this.publishedClips = publishedClips;
      this.clipsCurrentPage = 1;
    },


    /* ページネーションをクリックしたとき、ページ番号を更新 */
    clickVideosCallback: function(pageNum) {
      this.videosCurrentPage = Number(pageNum);
    },

    /* アーカイブの開始時間と終了時間をセットする */
    setArchiveDate: function(archive) {
      let created_at = archive['created_at'];   // 2019-09-07T08:59:47Z
      let duration = archive['duration'];       // 2h30m52s or 30m52s or 52s
      //console.log(created_at +" "+ duration);

      let pattern = /[hms]/;
      duration = duration.split(pattern);     // [hour,minutes,seconds,""] or [minutes,seconds,""] or [seconds,""]
      let hour=0, min=0, sec=0;

      if(duration.length === 4){
        hour = +duration[0];
        min = +duration[1];
        sec = +duration[2];
      }
      else if(duration.length === 3){
        min = +duration[0];
        sec = +duration[1];
      }
      else if(duration.length === 2){
        sec = +duration[0];
      }
      else {
        //console.log("Error : " + duration);
      }

      //console.log(hour +"h"+ min +"m"+ sec +"s");

      let m = moment(created_at);
      let fm = "YYYY-MM-DDTHH:mm:ss";
      let startDate = created_at;
      m.add({hours:hour-9,minutes:min,seconds:sec});
      let endMoment = m;
      let endDate = m.format(fm) + 'Z';

      this.archiveStartDate = startDate;
      this.archiveEndDate = endDate;
      //console.log("開始時刻: " + startDate);
      //console.log("終了時刻: "+ endDate);
      this.getArchiveClips();
      //this.datepickerStartedAt = startMoment.format("YYYY-MM-DD");
      //this.datepickerEndedAt = endMoment.format("YYYY-MM-DD");
    },


    /* ウィンドウのサイズを定期的に取得する */
    setWindowWidth: _.debounce(function() {
      // data にリサイズ後のウィンドウ幅を代入
      this.width = window.innerWidth;
    }, 300),

    setResponsiveItems: function() {
      if(this.width >= 1200) {
        this.videosParPage = 4;
        this.followsParPage = 12;
        this.timelineParPage = 7;
      }
      else if(this.width >= 1000) {
        this.videosParPage = 3;
        this.followsParPage = 10;
        this.timelineParPage = 5;
      }
      else if(this.width >= 800) {
        this.videosParPage = 2;
        this.followsParPage = 8;
        this.timelineParPage = 3;
      }
      else if(this.width >= 550) {
        this.videosParPage = 2;
        this.followsParPage = 5;
        this.timelineParPage = 2;
      }
      else {
        this.videosParPage = 1;
        this.followsParPage = 3;
        this.timelineParPage = 2;
      }
    },

    editRecievedHighlight: function(clips) {
      this.timelineClips = [];
      this.totalClipSeconds = 0;
      clips = clips.split(',');
      for(let i=0; i<clips.length; i++) {
        console.log(clips[i]);
        this.getClipById(clips[i],i);
      }
      //console.log(this.timelineClips);
    },

    timelineCmp: function(a, b) {
      let cmp = 0;
      if(a.index > b.index){
        cmp = 1;
      }
      else if (a.index < b.index) {
        cmp = -1;
      }
      return cmp;
    },

    timelineCmpByEpoch: function(a, b) {
      let cmp = 0;
      if(a.created_epoch >= b.created_epoch) {
        cmp = 1;
      } else {
        cmp = -1;
      }
      return cmp;
    },

    appendClip: function(clip) {
      let timelineClip = JSON.parse(JSON.stringify(clip));
      let index = 0;
      //console.log("getClipById↓:成功");
      //console.log(response);
      timelineClip['isHover'] = false;
      timelineClip['index'] = index;
      app.timelineClips.push(timelineClip);
      app.addClipPlayTime(timelineClip['thumbnail_url']);
      app.timelineClips.sort(app.timelineCmp);
    },

    deleteClip: function(clip) {
      let newTimelineClips = [];
      for(let i=0 ;i<this.timelineClips.length; i++){
        if(this.timelineClips[i]['id'] == clip['id']) {
          this.subClipPlayTime(this.timelineClips[i]['thumbnail_url']);
        } else {
          newTimelineClips.push(this.timelineClips[i]);
        }
      }

      this.timelineClips = [];
      for(let i=0; i<newTimelineClips.length; i++) this.timelineClips.push(newTimelineClips[i]);
    },

    isSelectedClip: function(clip) {
      //console.log(clip);
      for(let i=0; i<this.timelineClips.length; i++){
        //console.log(this.timelineClips[i]['id'], clip['id']);
        if (this.timelineClips[i]['id'] == clip['id'])
          return true;
      }
      return false;
    },

    prevClip: function() {
      //console.log("先頭のインデックス: " + this.timelinePageIndex);
      if(this.timelinePageIndex !== 0){
        this.timelinePageIndex -= 1;
      }
    },

    nextClip: function() {
      if(this.timelinePageIndex !== Math.max(this.timelineClips.length-this.timelineParPage, 0)){
        this.timelinePageIndex += 1;
      }
    },

    addClipPlayTime: function(clipThumbnail) {
      let key = clipThumbnail.split('-preview-')[0]
      let file = key + ".mp4"
      //console.log(file);
      let video = document.createElement('video');
      video.src = file;

      video.ondurationchange = function() {
        let playtime = parseInt(this.duration);
        app.totalClipSeconds += playtime;
      }
    },

    subClipPlayTime: function(clipThumbnail) {
      let key = clipThumbnail.split('-preview-')[0]
      let file = key + ".mp4"
      //console.log(file);
      let video = document.createElement('video');
      video.src = file;

      video.ondurationchange = function() {
        let playtime = parseInt(this.duration);
        app.totalClipSeconds -= playtime;
      }
    },

    openTimelineModal: function(embed_url) {
      this.timelineEmbedUrl = embed_url;
      $('#timelineModal').modal();
    },

    removeTimelineClip: function(index) {
      //console.log(index);
      index += this.timelinePageIndex;
      //console.log(index);
      this.subClipPlayTime(this.timelineClips[index]['thumbnail_url']);

      let newClips = [];
      for(let i=0; i<this.timelineClips.length; i++){
        if(index === i) continue;
        newClips.push(this.timelineClips[i]);
      }

      this.timelineClips = [];
      for(let i=0; i<newClips.length; i++) this.timelineClips.push(newClips[i]);
    },

    movePrevTimelineClip: function(index) {
      index += this.timelinePageIndex;
      this.timelineClips[index]['isHover'] = false;
      if(index !== 0){
        this.timelineClips.splice(index-1, 2, this.timelineClips[index], this.timelineClips[index-1]);
      }
    },

    moveNextTimelineClip: function(index) {
      index += this.timelinePageIndex;
      this.timelineClips[index]['isHover'] = false;
      if(index !== this.timelineClips.length-1){
        this.timelineClips.splice(index, 2, this.timelineClips[index+1], this.timelineClips[index]);
      }
    },

    sortTimelineClipsByDatetime: function() {
      this.timelineClips.sort(this.timelineCmpByEpoch);
    },

    /* ダイジェスト動画の情報をDjangoに渡す */
    postDigestInfo: function() {
      //console.log(csrftoken);
      data = {
        "creator": username,
        "streamer": this.streamerName,
        "title": this.title,
        "length": this.totalClipSeconds,
        "transition": this.transition,
        "duration": this.duration,
        "num_clips": this.timelineClips.length,
        "clips": this.timelineClips,
        "is_drawtext": this.isDrawText,
        "fontsize": this.fontsize,
        "fontcolor": this.fontcolor,
        "borderw": this.borderw,
        "position": this.position,
        "fl_transition": this.isFLTransition
      }
      axios.post(studio_url, {data}, {
        headers: {
          'X-CSRFToken': csrftoken,
        },
      }).then(function(response) {
          //console.log(response);
          window.location.href = studio_url;
        })
        .catch(function(error) {
          //console.log(error);
          //console.log(error.response);
        });
    },

    setDigestURL: function(taskId){
      // S3のダイジェスト動画が保存されているフォルダ名
      var folderName = "digest";
      // S3から取り出すデータの「プレフィックス」を設定する
      var digestKey = encodeURIComponent(folderName) + '/output/' + username + '/' + taskId + '.mp4';
      s3.listObjects(
          {
            Prefix: digestKey,
          },
          function (err, data) {
            if(err){
              return alert('error: ' + err.message);
            }
            var href = this.request.httpRequest.endpoint.href;
            var bucketUrl = href + bucket_name + '/';
            //console.log(bucketUrl);
            //console.log(data);

            // digestKeyと一致するデータをvideoSrcに追加する
            for(let i=0; i<data.Contents.length; i++){
              if(digestKey === data.Contents[i]['Key']){
                app.digestUrl = bucketUrl + encodeURIComponent(digestKey);
              }
            }
          }
        );
    },

    getHighlightVideo: function(highlight) {
      // S3のダイジェスト動画が保存されているフォルダ名
      var folderName = "digest";
      // S3から取り出すデータの「プレフィックス」を設定する
      var digestKey = encodeURIComponent(folderName) + '/output/' + username + '/' + highlight.task_id + '.mp4';
      s3.listObjects(
        {
          Prefix: digestKey,
        },
        function (err, data) {
          if(err){
            return console.log('error: ' + err.message);
          }
          var href = this.request.httpRequest.endpoint.href;
          var bucketUrl = href + bucket_name + '/';
          //console.log(bucketUrl);
          //console.log(data);

          // digestKeyと一致するデータがあれば true
          let hasHighlightVideo = false;
          for(let i=0; i<data.Contents.length; i++){
            if(digestKey === data.Contents[i]['Key']){
              hasHighlightVideo = true;
            }
          }
          highlight.hasHighlightVideo = hasHighlightVideo;
          app.setHighlightStatus(highlight);
        }
      );
    },

    getHighlights: function() {
      axios.get(highlight_url, {
        params: {
          'creator': user_pk
        }
      })
      .then(function(response) {
        //console.log(response);
        app.highlights = response['data'];
        for(let i=0; i<app.highlights.length; i++) {
          app.getHighlightVideo(app.highlights[i]);
          app.getHighlightTask(app.highlights[i]);
        }
      })
      .catch(function(error) {
        console.log(error);
      });
    },

    setHighlightStatus: function(highlight) {
      if (highlight.status != "Expired") {
        if (highlight.hasHighlightVideo) {
          this.$set(highlight,"status","Available");
        }
        else if (highlight.hasHighlightTask) {
          let requested = Date.parse(highlight.created);
          let current = Date.now();
          let diff = (current - requested) / 1000;
          //console.log(requested + ", " + current + " diff:" + diff + "(" + (diff/3600) +" hours)");
          let diff_hours = diff / 3600;
          if (diff_hours >= 24 * 6) {
            this.$set(highlight,"status","Expired");
          }
        }
      }
    },

    getHighlightTask: function(highlight) {
      axios.get(task_url, {
        params: {
          'task_id': highlight.task_id
        }
      })
      .then(function(response) {
        //console.log(response);
        highlight.hasHighlightTask = true;
      })
      .catch(function(error) {
        console.log(error);
        highlight.hasHighlightTask = false;
      })
      .then(function() {
        app.setHighlightStatus(highlight);
      });
    },

    formatRequested: function(requested) {
      let date = new Date(requested);
      return date.toLocaleString("ja");
    },

    openClipModal: function(embedUrl) {
      this.clipEmbedUrl = embedUrl;
      $('#clipModal').modal();
    },

    openDigestModal: function(taskId) {
      //console.log(task_id);
      this.setDigestURL(taskId);
      $('#digestModal').modal();
    },

  },

  created() {
    // インスタンスを作成した後に、イベントリスナに登録
    window.addEventListener('resize', this.setWindowWidth, false);
  },
  mounted() {
    let m = moment();
    this.datepickerEndedAt = m.add(1,'days').format('YYYY-MM-DD');
    this.datepickerStartedAt = m.add(-7, 'days').format('YYYY-MM-DD');
    this.setResponsiveItems();
    $('[data-toggle="tooltip"]').tooltip();
    this.userName = username;
    if (this.userName.length != 0) {
      //console.log("login: " + this.userName);
      this.getClientId();
      this.getHighlights();
    }
    this.siteUrl = location.hostname;
    TwitchAPI.apiUrl = api_url;
    TwitchAPI.clientId = this.Client_Id;
    TwitchAPI.token = this.token;
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.setWindowWidth, false);
  },

});