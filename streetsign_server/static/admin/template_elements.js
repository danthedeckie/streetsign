	function itemlink(url, text, active) {
		return m('.item',
			m("a[href='" + url + "']",
				{config: m.route},
				text
			)
		)
	}

	function topmenu() {
		return m('.ui.menu', [
			m('.header.item', ['StreetSign']), 
			itemlink('/users', 'Users & Groups'),
			itemlink('/uploads', 'Uploaded Files'),
			itemlink('/feeds', 'Feeds'),
			itemlink('/posts', 'Posts'),
			itemlink('/screens', 'Screens'),
			m('.item.right.menu', ['Me', m('i.dropdown.icon'),
				m('.menu.transition.hidden', [
					m('.item', 'Preferences'),
					m('.item', 'Log Out')
				])
			])
		]);
	}

	function footer() {
		return m('.ui.inverted.segment', 'footer')
	}

	/* feed elements */

	function feed_newpost(feedid) {
		// TODO
		return m('button.ui.button.right.floated', [
			'New Post ',
			m('i.dropdown.icon','')
		]);
	}

	/* Dashboard stuff */

	function my_feeds(feeds) {
		feeds = feeds || _FEEDS;
		return m('.ui.card', [
			m('.content', [
				m('.header', 'My Feeds'),
			]),
			feeds.map(function(feed) {
				return m('.content', [
					m('a', feed.name),
					feed_newpost(feed.id)
				])
			}),
		]);
	}

	function my_posts(posts) {
		posts = posts || _POSTS;
		return m('.ui.card', [
			m('.content', [
				m('.header', 'My Posts'),
			]), posts.map(function(post) {
				return m('.content', [
					m('a', post.repr),
					m('button.ui.button.right.floated', 'Publish'),
				])
			}),
		]);
	}

	function posts_table(posts) {
		posts = posts || _POSTS;
		return m('table.ui.celled.table', [
			m('thead',m('tr',[
				m('th', 'Content'),
				m('th', 'Author'),
				m('th', 'Feed'),
				m('th', 'State'),
				m('th', '...')
			])),
			m('tbody', posts.map(function(post) {
				return m('tr', [
					m('td', post.repr()),
					m('td', post.author()),
					m('td', post.feed()),
					m('td', post.state()),
					m('td', m('button.ui.button','x')),
				])
			}))
		]);
	}

	function feeds_table(feeds) {
		feeds = feeds || _FEEDS;
		return m('table.ui.celled.table', [
			m('thead', m('tr', [
				m('th', 'Feed Name'),
				m('th', m('button.ui.button', 'New Feed'))
			])),
			m('tbody', feeds.map(function(feed) {
				return m('tr', [
					m('td', [
						m("a[href='/feeds/"+feed.id+"']", {config: m.route}, feed.name()),
						m('.ui.label', feed.post_count() + ' posts'),
						m('.ui.label', feed.active_post_count() + ' active'),
					]),
					m('td', [
						feed_newpost(feed.id),
						m('button.ui.button.right.floated', 'x')
					])
				])
			}))
		]);
	}


