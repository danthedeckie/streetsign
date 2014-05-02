{
    render: function(zone, data) {
        'use strict';

        console.log('making img (' + data.content.file_url + ')');
        return $('<div class="post post_image" style="'
                 + 'background-image: url(' + data.content.file_url + ');'
                 + 'background-repeat:no-repeat;'
                 + 'background-size:contain;'
                 + 'background-position: center center;'
                 + '"></div>').prependTo(zone);
    }
}
