
var TwitchAPI = {
    apiUrl: "http://localhost:8000/twitchapi",
    clientId: '',
    token: '',
    is_token: false,

    /* 文字列を'YYYY-MM-DD'に変換したものを返す */
    customformat: function(value) {
        return moment(value).format('YYYY-MM-DD');
    },

    getRequest: async function(url, params) {
        if (this.is_token) {
            return await axios.get(url, {
                headers: {
                    'Client-ID': this.clientId,
                    'Authorization': `Bearer ${this.token}`
                },
                params: params
            });
        } else {
            return await axios.get(this.apiUrl, {
                params: {
                    'url': url,
                    'params': params
                }
            });
        }
    },

    /* ストリーマの名前からストリーマIDを取得する */
    getClientId: async function(streamerName) {
        let url = 'https://api.twitch.tv/helix/users';
        let params = {
            'login': streamerName
        };

        return await this.getRequest(url, params);
    },

    /* ユーザがフォローしている配信者を取得する */
    getFollows: async function(clientId) {
        let url = 'https://api.twitch.tv/helix/follows';
        let params = {
            'from_id': clientId,
            'first': 100
        };

        return await this.getRequest(url, params);
    },

    /* ユーザIDからユーザの情報を取得する */
    getUsers: async function(userIds) {
        let url = 'https://api.twitch.tv/helix/users';
        let params = {
            'id': userIds
        }

        return await this.getRequest(url, params);
    },

    /* 配信者のIDを指定して、その配信のクリップを取得する */
    getClips: async function(streamerId, datepickerStartedAt, datepickerEndedAt) {
        let url = 'https://api.twitch.tv/helix/clips';
        let params = {
            'broadcaster_id': streamerId,
            'started_at': this.customformat(datepickerStartedAt) + 'T00:00:00Z', // RFC3339 format (ex:'2019-08-31T00:00:00Z')
            'ended_at': this.customformat(datepickerEndedAt) + 'T00:00:00Z',     // RFC3339 format
            'first': 27,
        };

        return await this.getRequest(url, params);
    },

    /* クリップのIDを指定してクリップを取得する */
    getClipById: async function(clip_id) {
        let url = 'https://api.twitch.tv/helix/clips';
        let params = {
            'id': clip_id,
        };

        return await this.getRequest(url, params);
    },

    /* afterで指定されているクリップデータを追加で読み込む */
    getAfterClips: async function(streamerId, datepickerStartedAt, datepickerEndedAt, clipsAfter) {
        let url = 'https://api.twitch.tv/helix/clips';
        let params = {
            'broadcaster_id': streamerId,
            'started_at': this.customformat(datepickerStartedAt) + 'T00:00:00Z', // RFC3339 format (ex:'2019-08-31T00:00:00Z')
            'ended_at': this.customformat(datepickerEndedAt) + 'T00:00:00Z',     // RFC3339 format
            'first': 27,
            'after': clipsAfter,
        };

        return await this.getRequest(url, params);
    },

    /* 配信アーカイブを取得する */
    getVideos: async function(streamerId) {
        let url = 'https://api.twitch.tv/helix/videos';
        let params = {
            'user_id': streamerId,
            'type': 'archive',
            'first': 100,
        };

        return await this.getRequest(url, params);
    },

    /* 配信者のIDを指定して、その配信のクリップを取得する */
    getArchiveClips: async function(streamerId, archiveStartDate, archiveEndDate) {
        let url = 'https://api.twitch.tv/helix/clips';
        let params = {
            'broadcaster_id': streamerId,
            'started_at': archiveStartDate, // RFC3339 format (ex:'2019-08-31T00:00:00Z')
            'ended_at': archiveEndDate,     // RFC3339 format
            'first': 27,
        };

        return await this.getRequest(url, params);
    },
}
