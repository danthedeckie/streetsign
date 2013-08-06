/************************************************************

    StreetSign Digital Signage Project
     (C) Copyright 2013 Daniel Fairhead

    StreetSign is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    StreetSign is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with StreetSign.  If not, see <http://www.gnu.org/licenses/>.

    ---------------------------------
    global vars defaults.

*************************************************************/

// TODO: get these from somewhere?
//'use strict';
UPDATE_ZONES_TIMER = 6000; // how often to check for new posts?
REFRESH_PAGE_TIMER = 3600000; // how often to reboot the page? this is every hour...

window.post_types = {};
window.zones = [];
