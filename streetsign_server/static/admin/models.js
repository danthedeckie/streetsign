/* Models */

var Post = function(data) {
	this.type = m.prop(data.type);
	this.content = m.prop(data.content);
	this.repr = m.prop(data.repr);
	this.feed = m.prop(data.feedid);
	this.state = m.prop(data.state);
	this.author = m.prop(data.author);
	this.published = m.prop(data.published);
	this.status = m.prop(data.status);
};

Post.list = function(data) {
	return m.request({
		method:'GET',
		url:'/api/posts',
		data: data,
		type: Post,
		unwrapSuccess: function(resp) {
			return resp.posts;
		}
	});
}

var Feed = function(data) {
	this.id = data.id;
	this.name = m.prop(data.name);
	this.post_types = m.prop(data.post_types);
	this.post_count = m.prop(data.post_count);
	this.active_post_count = m.prop(data.active_post_count);
};

Feed.list = function(data) {
	
	return m.request({
		method:'GET',
		url:'/api/feeds',
		data: data,
		type: Feed,
		unwrapSuccess: function(resp) {
			return resp.feeds;
		}
	});
}

Feed.get = function(feedid) {
	return m.request({
		method: 'GET',
		url: '/api/feed/' + feedid,
		type: Feed,
	})
}
