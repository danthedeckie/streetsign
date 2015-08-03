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
from streetsign_server.views.utils import admin_only, registered_users_only, \
                                          permission_denied, not_found

import peewee

from streetsign_server import app
from streetsign_server.models import User, Group, Post, UserGroup, InvalidPassword

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
    except peewee.DoesNotExist:
        flash('Invalid username or password! Sorry!')
    except InvalidPassword:
        flash('Invalid username or password! Sorry!')

    # TODO: add appropriate HTTP status codes...

    return redirect(request.referrer if request.referrer else '/')

@app.route('/logout', methods=['POST'])
def logout():
    ''' log out, remove session cookies, etc. '''

    #return_to = request.form.get('from', 'index')

    # delete the session from the database:
    try:
        user_session.logout()
    except Exception as e:
        print 'Error Logging Out: %s' % e
        flash('error logging out. That is odd')

    # return to dashboard
    return redirect('/')

##################################################################
# User Management:

@app.route('/users_and_groups', methods=['GET', 'POST'])
@admin_only('POST')
@registered_users_only('GET')
def users_and_groups():
    ''' list of all users and groups (HTML page). '''

    if request.method == 'POST':
        action = request.form.get('action', 'creategroup')

        if action == 'creategroup':
            if not request.form.get('name', '').strip():
                flash("I'm not making you an un-named group!")
                return redirect(url_for('users_and_groups'))

            Group.create(name=request.form.get('name', 'blank').strip())


    return render_template('users_and_groups.html',
                           users=User.select(),
                           groups=Group.select())

@app.route('/users/<int:userid>', methods=['GET', 'POST'])
@app.route('/users/-1', methods=['GET', 'POST'])
@registered_users_only('GET')
def user_edit(userid=-1):
    ''' edit one user.  Admins can edit any user, but other users
        can only edit themselves. if userid is -1, create a new user. '''

    try:
        current_user = user_session.get_user()
    except user_session.NotLoggedIn as e:
        flash("Sorry, you're not logged in!")
        return permission_denied("You're not logged in!")

    userid = int(userid)

    if userid != -1:
        try:
            user = User.get(id=userid)
        except User.DoesNotExist:
            return not_found(title="User doesn't exist",
                             message="Sorry, that user does not exist!")
    else:
        if not current_user.is_admin:
            flash('Sorry! Only admins can create new users!')
            return permission_denied("Admins only!")

        user = User() #pylint: disable=no-value-for-parameter

        user.loginname = 'new'
        user.displayname = 'New User'
        user.emailaddress = '...'

    if request.method == 'POST':
        action = request.form.get('action', 'none')
        if action == 'update':
            if current_user != user and not current_user.is_admin:
                return permission_denied("Sorry, you may not edit this user.")

            oldname = user.loginname
            user.loginname = request.form.get('loginname', user.loginname)

            user.displayname = request.form.get('displayname',
                                                user.displayname)
            user.emailaddress = request.form.get('emailaddress',
                                                 user.emailaddress)

            if user.id != current_user.id:
                user.is_admin = request.form.get('is_admin', False)

            # Set password:

            newpass = request.form.get('newpass', '') if \
                        request.form.get('newpass', '') \
                        == request.form.get('conf_newpass', '2') else False

            if newpass:
                if current_user.confirm_password(request.form.get('currpass', '')):
                    user.set_password(newpass)
                    if userid != -1:
                        flash('Password changed.')
                else:
                    if not request.form.get('currpass',''):
                        flash("You need to enter your current password"
                              " as well as (2x) the new one.")
                    else:
                        flash('Your current password was wrong!')

            else: # passwords either empty (so don't change) or don't match!
                if request.form.get('newpass', '') != '':
                    flash('Passwords don\'t match!')

            # set groups:

            if current_user.is_admin:
                user.set_groups(request.form.getlist('groups'))

            # save:

            try:
                user.save()
                if userid == -1:
                    flash('New user created.')
                    return redirect(url_for('user_edit', userid=user.id))
                else:
                    flash('Saved')

            except peewee.IntegrityError as err:
                flash(str(err))

        elif action == 'delete':
            if not current_user.is_admin:
                return permission_denied("Sorry, only admins can delete users.")

            if user.id == current_user.id:
                flash('Sorry! You cannot delete yourself!')
                return redirect(url_for('users_and_groups'))

            try:
                user.delete_instance(recursive=True)
            except User.DoesNotExist:
                flash("Non-existant user!")
                return not_found(title="User Not Found",
                                 message="Sorry, you cannot delete"
                                         " that user, as they don't exist!")

            flash('User: %s deleted. (And all their posts)' % user.displayname)
            return redirect(url_for('users_and_groups'))

    users_posts = Post.select().where(Post.author == user) \
                               .order_by(Post.write_date.desc()) \
                               .limit(10)

    return render_template('user.html',
                           allgroups=Group.select(),
                           posts=users_posts, user=user)


@app.route('/group/<int:groupid>', methods=['GET', 'POST'])
@registered_users_only('GET')
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
            return redirect(url_for('users_and_groups'))

        if request.form.get('action', 'none') == 'delete':
            UserGroup.delete().where(UserGroup.group == thisgroup).execute()
            thisgroup.delete_instance()
            flash('group:'+ thisgroup.name +' deleted.')
            return redirect(url_for('users_and_groups'))

        if request.form.get('action', 'none') == 'update':
            thisgroup.name = request.form.get('groupname', thisgroup.name)
            thisgroup.save()

            groupusers = request.form.getlist('groupusers')
            thisgroup.set_users(groupusers)
            flash('saved')

    return render_template('group.html', group=thisgroup, allusers=User.select())
