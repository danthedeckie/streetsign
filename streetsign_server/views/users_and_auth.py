# -*- coding: utf-8 -*-
# StreetSign Digital Signage Project
#     (C) Copyright 2013 Daniel Fairhead
#
#    StreetSign is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    StreetSign is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with StreetSign.  If not, see <http://www.gnu.org/licenses/>.
#
#    ---------------------------------
'''
    streetsign_server.views.users_and_auth
    --------------------------------------

    Views for Working with users and passwords, and user-groups.

'''


from flask import render_template, url_for, request, redirect, flash
import streetsign_server.user_session as user_session
from streetsign_server import app
from streetsign_server.models import User, Group, Post, UserGroup

# pylint: disable=no-member


@app.route('/login', methods=['POST'])
def login():
    ''' log a user into the system, set session cookies, set up database
        session row, or not, if wrong password. '''

    # TODO: is using the request.endpoint the best way to do this?
    #       would it be better to use an absolute URL?  I dunno if this
    #       is better against XSS?

    #return_to = request.form.get('from', 'index')
    try:
        user_session.login(request.form['username'], request.form['password'])
    except:
        flash('Invalid username or password! Sorry!')

    return redirect(request.referrer)

@app.route('/logout', methods=['POST'])
def logout():
    ''' log out, remove session cookies, etc. '''

    #return_to = request.form.get('from', 'index')

    # delete the session from the database:
    try:
        user_session.logout()
    except:
        flash('error logging out. That is odd')

    # return to where we were.
    return redirect(request.referrer)

##################################################################
# User Management:

@app.route('/users')
def users():
    ''' list of all users (HTML page). '''
    return render_template('users.html', users=User.select())

@app.route('/users/<int:userid>', methods=['GET', 'POST'])
@app.route('/users/-1', methods=['GET', 'POST'])
def user(userid=-1):
    ''' edit one user.  Admins can edit any user, but other users
        can only edit themselves. if userid is -1, create a new user. '''

    try:
        current_user = user_session.get_user()
    except user_session.NotLoggedIn as e:
        flash("Sorry, you're not logged in!")
        return redirect(url_for('index'))

    userid = int(userid)

    if userid != -1:
        user = User.get(id=userid)
    else:
        if not current_user.is_admin:
            flash('Sorry! Only admins can create new users!')
            return redirect(url_for('users'))

        user = User()
        user.loginname = 'new'
        user.displayname = 'New User'
        user.emailaddress = '...'


    if request.method == 'POST':
        action = request.form.get('action', 'none')
        if action == 'update':
            if current_user != user and not current_user.is_admin:
                flash('Sorry! You cannot edit this user!')
                return render_template('user.html', user=user)
            try:
                oldname = user.loginname
                user.loginname = request.form.get('loginname', user.loginname)
            except:
                user.loginname = oldname if oldname else 'NEW'
                flash('Sorry! You cannot have that loginname.' \
                      ' Someone else does')

            user.displayname = request.form.get('displayname',
                                                user.displayname)
            user.emailaddress = request.form.get('emailaddress',
                                                 user.emailaddress)

            if not user.id == current_user.id:
                user.is_admin = request.form.get('is_admin', False)

            newpass = request.form.get('newpass', '') if \
                        request.form.get('newpass', '') \
                        == request.form.get('conf_newpass', '2') else False

            if newpass:
                if current_user.confirm_password(request.form.get('currpass', '')):
                    user.set_password(request.form.get('newpass'))
                    flash('password changed')
                else:
                    flash('Your password was wrong!')
            else:
                if not request.form.get('newpass', '') == '':
                    flash('invalid password!')

            if current_user.is_admin:
                user.set_groups(request.form.getlist('groups'))

            user.save()
            flash('Updated.')
            if userid == -1:
                return redirect(url_for('user', userid=user.id))
        elif action == 'delete':
            if not current_user.is_admin:
                flash('Sorry! Only admins can delete users!')
                return redirect(request.referrer)

            if user.id == current_user.id:
                flash('Sorry! You cannot delete yourself!')
                return redirect(request.referrer)

            user.delete_instance(recursive=True)
            flash('User:' + user.displayname + ' deleted. (And all their posts)')
            return redirect(request.referrer)

    users_posts = Post.select().where(Post.author == user) \
                               .order_by(Post.write_date.desc()) \
                               .limit(10)

    return render_template('user.html',
                            allgroups=Group.select(),
                            posts=users_posts, user=user)


@app.route('/groups', methods=['GET', 'POST'])
def groups():
    ''' (HTML) user-groups list, and creation of new ones. '''

    if request.method == 'POST':
        if not user_session.is_admin():
            flash('Only Admins can do this!')
            return redirect(url_for('groups'))

        action = request.form.get('action', 'create')

        if action == 'create':
            if not request.form.get('name', '').strip():
                flash("I'm not making you an un-named group!")
                return redirect(url_for('groups'))
            Group(name=request.form.get('name', 'blank').strip()).save()

    return render_template('groups.html', groups=Group.select())

@app.route('/group/<int:groupid>', methods=['GET', 'POST'])
def group(groupid):
    ''' edit one user group. '''

    try:
        thisgroup = Group.get(id=groupid)
    except:
        flash('Invalid group ID')
        return redirect(request.referrer)

    if request.method == 'POST':
        if not user_session.is_admin():
            flash('Only Admins can do this!')
            return redirect(url_for('groups'))

        if request.form.get('action', 'none') == 'delete':
            UserGroup.delete().where(UserGroup.group == thisgroup).execute()
            thisgroup.delete_instance()
            flash('group:'+ thisgroup.name +' deleted.')
            return redirect(url_for('groups'))

        if request.form.get('action', 'none') == 'update':
            thisgroup.name = request.form.get('groupname', thisgroup.name)
            thisgroup.save()

            groupusers = request.form.getlist('groupusers')
            thisgroup.set_users(groupusers)
            flash('saved')

    return render_template('group.html', group=thisgroup, allusers=User.select())
