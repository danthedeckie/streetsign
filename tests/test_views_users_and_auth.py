'''
    Testing user creation/deletion/modification.
'''

# pylint: disable=too-many-public-methods, missing-docstring, invalid-name

import sys
import os

sys.path.append(os.path.dirname(__file__) + '/..')

from flask import url_for

import streetsign_server
import streetsign_server.models as models
from streetsign_server.models import User, Group

from streetsign_server.views.users_and_auth import *

from unittest_helpers import StreetSignTestCase

USERNAME = 'test'
USERPASS = '123'

ADMINNAME = 'admin'
ADMINPASS = '42'

class BasicUsersTestCase(StreetSignTestCase):
    def setUp(self):
        super(BasicUsersTestCase, self).setUp()
        self.user = User(loginname=USERNAME,
                         emailaddress='test@streetsign.org.uk',
                         is_admin=False)
        self.user.set_password(USERPASS)
        self.user.save()


        self.admin = User(loginname=ADMINNAME,
                          emailaddress='test@adstreetsign.org.uk',
                          is_admin=True)
        self.admin.set_password(ADMINPASS)
        self.admin.save()

class ChangingPasswords(BasicUsersTestCase):
    ''' Testing Passwords can be changed sensibly. '''

    def test_logged_out_cannot_see_users(self):
        with self.ctx():
            self.validate(url_for('users_and_groups'), code=403)

    def test_logged_out_cannot_see_user(self):
        with self.ctx():
            self.validate(url_for('user_edit', userid=self.user.id), code=403)
            self.validate(url_for('user_edit', userid=self.admin.id), code=403)

    def test_logged_out_cannot_set_password(self):
        with self.ctx():
            resp = self.client.post(url_for('user_edit', userid=self.user.id),
                                    data={"action":"update",
                                          "newpass": "200",
                                          "conf_newpass": "200"},
                                    follow_redirects=True)

        self.assertIn("Permission Denied", resp.data)

        # and make sure the password didn't get changed!

        usernow = User.get(id=self.user.id)
        self.assertEqual(usernow.passwordhash, self.user.passwordhash)

    def test_cannot_change_password_without_current_password(self):
        self.login(USERNAME, USERPASS)

        with self.ctx():
            resp = self.client.post(url_for('user_edit', userid=self.user.id),
                                    data={"action":"update",
                                          "newpass": "200",
                                          "conf_newpass": "200"},
                                    follow_redirects=True)

        self.assertNotIn("Password changed", resp.data)
        self.assertIn("You need to enter your current password", resp.data)

        usernow = User.get(id=self.user.id)
        self.assertEqual(usernow.passwordhash, self.user.passwordhash)


    def test_cannot_change_password_with_wrong_current_password(self):
        self.login(USERNAME, USERPASS)

        with self.ctx():
            resp = self.client.post(url_for('user_edit', userid=self.user.id),
                                    data={"action":"update",
                                          "newpass": "200",
                                          "conf_newpass": "200",
                                          "currpass": "bananas"},
                                    follow_redirects=True)

        self.assertNotIn("Password changed", resp.data)
        self.assertIn("Your current password was wrong", resp.data)

        usernow = User.get(id=self.user.id)
        self.assertEqual(usernow.passwordhash, self.user.passwordhash)

    def test_cannot_change_password_with_differing_inputs(self):
        self.login(USERNAME, USERPASS)

        with self.ctx():
            resp = self.client.post(url_for('user_edit', userid=self.user.id),
                                    data={"action":"update",
                                          "newpass": "200",
                                          "conf_newpass": "201",
                                          "currpass": USERPASS},
                                    follow_redirects=True)

        self.assertNotIn("Password changed", resp.data)
        self.assertIn("Passwords don&#39;t match", resp.data)

        usernow = User.get(id=self.user.id)
        self.assertEqual(usernow.passwordhash, self.user.passwordhash)


    def test_can_change_own_password(self):
        self.login(USERNAME, USERPASS)

        with self.ctx():
            resp = self.client.post(url_for('user_edit', userid=self.user.id),
                                    data={"action":"update",
                                          "newpass": "200",
                                          "currpass": USERPASS,
                                          "conf_newpass": "200"},
                                    follow_redirects=True)

        self.assertIn("Password changed", resp.data)

        usernow = User.get(id=self.user.id)
        self.assertNotEqual(usernow.passwordhash, self.user.passwordhash)

    def test_cannot_change_other_users_password(self):

        user2 = User(loginname="user2",
                     emailaddress='test@streetsign.org.uk',
                     is_admin=False)
        user2.set_password("userpass2")
        user2.save()

        self.login(USERNAME, USERPASS)

        with self.ctx():
            resp = self.client.post(url_for('user_edit', userid=user2.id),
                                    data={"action":"update",
                                          "newpass": "200",
                                          "conf_newpass": "200",
                                          "currpass": USERPASS},
                                    follow_redirects=True)

        self.assertIn("Permission Denied", resp.data)
        self.assertEquals(resp.status_code, 403)

        usernow = User.get(id=user2.id)
        self.assertEqual(usernow.passwordhash, user2.passwordhash)

    def test_cannot_change_other_users_password_even_with_their_currpass(self):

        user2 = User(loginname="user2",
                     emailaddress='test@streetsign.org.uk',
                     is_admin=False)
        user2.set_password("userpass2")
        user2.save()

        self.login(USERNAME, USERPASS)

        with self.ctx():
            resp = self.client.post(url_for('user_edit', userid=user2.id),
                                    data={"action":"update",
                                          "newpass": "200",
                                          "conf_newpass": "200",
                                          "currpass": "userpass2"},
                                    follow_redirects=True)

        self.assertIn("Permission Denied", resp.data)
        self.assertEquals(resp.status_code, 403)

        usernow = User.get(id=user2.id)
        self.assertEqual(usernow.passwordhash, user2.passwordhash)

    def test_admin_can_change_users_password(self):
        self.login(ADMINNAME, ADMINPASS)

        with self.ctx():
            resp = self.client.post(url_for('user_edit', userid=self.user.id),
                                    data={"action":"update",
                                          "newpass": "200",
                                          "currpass": ADMINPASS,
                                          "conf_newpass": "200"},
                                    follow_redirects=True)

        self.assertIn("Password changed", resp.data)

        usernow = User.get(id=self.user.id)
        self.assertNotEqual(usernow.passwordhash, self.user.passwordhash)

    def test_admin_can_change_own_password(self):
        self.login(ADMINNAME, ADMINPASS)

        with self.ctx():
            resp = self.client.post(url_for('user_edit', userid=self.admin.id),
                                    data={"action":"update",
                                          "newpass": "200",
                                          "currpass": ADMINPASS,
                                          "conf_newpass": "200"},
                                    follow_redirects=True)

        self.assertIn("Password changed", resp.data)

        usernow = User.get(id=self.admin.id)
        self.assertNotEqual(usernow.passwordhash, self.admin.passwordhash)


class CreatingUsersTestCase(BasicUsersTestCase):
    ''' Admin only can create new users. '''

    def post_create_request(self, username="user2", userid=-1, **kwargs):
        data = {"action": "update",
                "loginname": username,
                "newpass": "123",
                "conf_newpass": "123",
               }
        data.update(kwargs)

        with self.ctx():
            return self.client.post(url_for('user_edit', userid=userid),
                                    data=data, follow_redirects=True)

    def test_logged_out_cannot_create_user(self):
        resp = self.post_create_request()
        self.assertEqual(resp.status_code, 403)

    def test_normal_user_cannot_create_user(self):
        self.login(USERNAME, USERPASS)
        resp = self.post_create_request()
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_create_user(self):
        # should not yet exist:
        with self.assertRaises(User.DoesNotExist):
            User.get(loginname="user2")

        self.login(ADMINNAME, ADMINPASS)
        resp = self.post_create_request(currpass=ADMINPASS)
        self.assertEqual(resp.status_code, 200)

        User.get(loginname="user2")

    def test_admin_needs_password_to_create_user(self):
        with self.assertRaises(User.DoesNotExist):
            User.get(loginname="user2")

        self.login(ADMINNAME, ADMINPASS)
        resp = self.post_create_request()
        self.assertIn("You need to enter your current password", resp.data)

        with self.assertRaises(User.DoesNotExist):
            User.get(loginname="user2")

    def test_cannot_have_empty_password(self):
        with self.assertRaises(User.DoesNotExist):
            User.get(loginname="user2")

        self.login(ADMINNAME, ADMINPASS)
        resp = self.post_create_request(currpass=ADMINPASS,
                                        newpass='',
                                        conf_newpass='')
        self.assertIn("Cannot Save", resp.data)
        self.assertIn("passwordhash", resp.data)

        with self.assertRaises(User.DoesNotExist):
            User.get(loginname="user2")

    def test_new_user_passwords_must_match(self):
        with self.assertRaises(User.DoesNotExist):
            User.get(loginname="user2")

        self.login(ADMINNAME, ADMINPASS)
        resp = self.post_create_request(currpass=ADMINPASS,
                                        newpass='stuff',
                                        conf_newpass='42')
        self.assertIn("Passwords don&#39;t match", resp.data)

        with self.assertRaises(User.DoesNotExist):
            User.get(loginname="user2")



    def test_cannot_have_matching_usernames(self):
        user2 = User(loginname='user2',
                     emailaddress='test@streetsign.org.uk',
                     is_admin=False)
        user2.set_password(USERPASS)
        user2.save()

        # if this get works, then the user exists:
        usernow = User.get(loginname="user2")
        self.assertEqual(user2.id, usernow.id)

        self.login(ADMINNAME, ADMINPASS)
        resp = self.post_create_request(currpass=ADMINPASS,
                                        newpass='not42', conf_newpass='not42')
        self.assertIn("Username already exists", resp.data)

        # and just make sure we didn't delete them, or set their password...

        usernew = User.get(loginname="user2")
        self.assertEqual(usernow.passwordhash, usernew.passwordhash)


class DeletingUsers(BasicUsersTestCase):
    ''' Only admin can delete users, and not themselves. '''

    def setUp(self):
        super(DeletingUsers, self).setUp()

        self.user2 = User(loginname='user2',
                          emailaddress='test@streetsign.org.uk',
                          is_admin=False)
        self.user2.set_password(USERPASS)
        self.user2.save()

    def post_delete_request(self, userid=False, **kwargs):
        data = {}
        data.update(kwargs)

        if userid == False:
            userid = self.user2.id

        with self.ctx():
            return self.client.delete(url_for('user_edit', userid=userid),
                                      data=data,
                                      follow_redirects=True)

    def test_logged_out_cannot_delete_user(self):
        resp = self.post_delete_request()
        self.assertEqual(resp.status_code, 403)
        User.get(id=self.user2.id)

    def test_normal_user_cannot_delete_user(self):
        self.login(USERNAME, USERPASS)
        resp = self.post_delete_request()
        self.assertEqual(resp.status_code, 403)
        User.get(id=self.user2.id)

    def test_normal_user_cannot_delete_self(self):
        self.login(USERNAME, USERPASS)
        resp = self.post_delete_request(userid=self.user.id)
        self.assertEqual(resp.status_code, 403)

        User.get(id=self.user.id)

    def test_normal_user_cannot_delete_admin(self):
        self.login(USERNAME, USERPASS)
        resp = self.post_delete_request(userid=self.admin.id)
        self.assertEqual(resp.status_code, 403)

        User.get(id=self.admin.id)

    def test_admin_can_delete_user(self):
        self.login(ADMINNAME, ADMINPASS)
        resp = self.post_delete_request()
        self.assertEqual(resp.status_code, 200)

        with self.assertRaises(User.DoesNotExist):
            User.get(id=self.user2.id)

    def test_admin_cannot_delete_self(self):
        self.login(ADMINNAME, ADMINPASS)
        resp = self.post_delete_request(userid=self.admin.id)
        self.assertIn("You cannot delete yourself", resp.data)

        User.get(id=self.admin.id)

    def test_admin_cannot_delete_nonexistant_user(self):
        self.login(ADMINNAME, ADMINPASS)
        resp = self.post_delete_request(userid=200)
        self.assertEqual(resp.status_code, 404)

    def test_normal_user_cannot_delete_nonexistant_user(self):
        self.login(USERNAME, USERPASS)
        resp = self.post_delete_request(userid=200)
        self.assertEqual(resp.status_code, 404)

    def when_user_deleted_posts_also_deleted(self):
        self.login(ADMINNAME, ADMINPASS)
        # TODO
        pass

class UserUpdatesTestCase(BasicUsersTestCase):
    def post_update_request(self, userid=None, **kwargs):
        if userid == None:
            userid = self.user.id

        data = {}
        data.update(kwargs)

        with self.ctx():
            return self.client.post(url_for('user_edit', userid=userid),
                                    data=data, follow_redirects=True)

    def test_logged_out_cannot_update_someone(self):
        resp = self.post_update_request(loginname='Banana!')
        self.assertEqual(resp.status_code, 403)

    def test_cannot_change_other_users_details(self):
        resp = self.post_update_request(userid=self.admin.id,
                                        loginname='Banana!')
        self.assertEqual(resp.status_code, 403)

    def test_logged_in_can_change_own_loginname(self):
        self.login(USERNAME, USERPASS)
        self.post_update_request(loginname='Banana!')

        usernow = User.get(id=self.user.id)
        self.assertEqual(usernow.loginname, 'Banana!')

    def test_logged_in_cannot_set_empty_loginname(self):
        self.login(USERNAME, USERPASS)
        self.post_update_request(loginname='')

        usernow = User.get(id=self.user.id)
        self.assertEqual(usernow.loginname, USERNAME)

    def test_logged_in_can_change_own_displayname(self):
        self.login(USERNAME, USERPASS)
        self.post_update_request(displayname='Banana!')

        usernow = User.get(id=self.user.id)
        self.assertEqual(usernow.displayname, 'Banana!')

    def test_logged_in_can_change_own_emailaddress(self):
        self.login(USERNAME, USERPASS)
        self.post_update_request(emailaddress='test2@streetsign.org.uk')

        usernow = User.get(id=self.user.id)
        self.assertEqual(usernow.emailaddress, 'test2@streetsign.org.uk')

    def test_emailaddress_must_be_valid(self):
        self.login(USERNAME, USERPASS)
        resp = self.post_update_request(emailaddress='BANANA!!!!')

        self.assertIn('not a valid emailaddress', resp.data)

        usernow = User.get(id=self.user.id)
        self.assertEqual(usernow.emailaddress, 'test@streetsign.org.uk')

    def test_normal_user_cannot_set_self_admin(self):
        self.login(USERNAME, USERPASS)
        resp = self.post_update_request(is_admin=True)

        usernow = User.get(id=self.user.id)
        self.assertEqual(usernow.is_admin, False)

    def test_normal_user_cannot_set_other_to_admin(self):
        user2 = User(loginname="user2",
                     emailaddress='test@streetsign.org.uk',
                     is_admin=False)
        user2.set_password("userpass2")
        user2.save()

        self.login(USERNAME, USERPASS)
        resp = self.post_update_request(userid=user2.id, is_admin=True)

        self.assertEqual(resp.status_code, 403)

        usernow = User.get(id=user2.id)
        self.assertEqual(usernow.is_admin, False)

    def test_normal_user_cannot_unset_admin(self):
        self.login(USERNAME, USERPASS)
        resp = self.post_update_request(userid=self.admin.id, is_admin=False)

        self.assertEqual(resp.status_code, 403)

        adminnow = User.get(id=self.admin.id)
        self.assertEqual(adminnow.is_admin, True)

    def test_admin_can_make_admin(self):
        self.assertFalse(self.user.is_admin)
        self.login(ADMINNAME, ADMINPASS)
        resp = self.post_update_request(userid=self.user.id, is_admin=True)

        usernow = User.get(id=self.user.id)
        self.assertTrue(usernow.is_admin)

    def test_admin_can_make_admin_with_on(self):
        self.assertFalse(self.user.is_admin)
        self.login(ADMINNAME, ADMINPASS)
        resp = self.post_update_request(userid=self.user.id, is_admin="on")

        usernow = User.get(id=self.user.id)
        self.assertTrue(usernow.is_admin)



    def test_admin_can_unset_admin(self):
        self.assertFalse(self.user.is_admin)
        self.user.is_admin = True
        self.user.save()

        usernow = User.get(id=self.user.id)
        self.assertTrue(usernow.is_admin)

        self.login(ADMINNAME, ADMINPASS)
        resp = self.post_update_request(userid=self.user.id, is_admin=False)

        usernow = User.get(id=self.user.id)
        self.assertFalse(usernow.is_admin)

    def test_admin_cannot_unadmin_self(self):
        self.login(ADMINNAME, ADMINPASS)
        resp = self.post_update_request(userid=self.admin.id, is_admin=False)

        adminnow = User.get(id=self.admin.id)
        self.assertEqual(adminnow.is_admin, True)

    ####################

    def create_group(self, name):
        g = Group(name=name)
        g.save()
        return g

    def test_cannot_set_own_groups(self):
        g1 = self.create_group('g1')

        self.assertEqual(self.user.groups(), [])
        self.login(USERNAME, USERPASS)

        self.post_update_request(userid=self.user.id, groups=[g1.id])

        usernow = User.get(id=self.user.id)
        self.assertEqual(usernow.groups(), [])

    def test_admin_can_set_groups(self):
        g1 = self.create_group('g1')

        self.assertEqual(self.user.groups(), [])
        self.login(ADMINNAME, ADMINPASS)

        self.post_update_request(userid=self.user.id, groups=[g1.id])

        usernow = User.get(id=self.user.id)
        self.assertEqual(usernow.groups(), [g1])


'''
    TODO:



    def test_loginname_bad_chars(self):

    def test_displayname_bad_chars(self):

    def test_emailaddress_bad_chars(self):

    def test_cannot_set_own_groups(self):

    def test_cannot_set_others_groups(self):

    def test_admin_can_set_own_groups(self):

    def test_admin_cannot_set_invalid_groups(self):
'''

class UserGroupsTestCase(BasicUsersTestCase):

    def post_create_group(self, name='new group', **kwargs):
        data = {"action": "creategroup", "name": name}
        data.update(kwargs)

        with self.ctx():
            return self.client.post(url_for('users_and_groups'),
                                    data=data, follow_redirects=True)

    def post_update_group(self, gid, name):
        # TODO
        pass

    def group_exists(self, name='new group'):
        try:
            Group.get(name=name)
            return True
        except Group.DoesNotExist:
            return False

    def test_logged_out_cannot_create_group(self):
        self.assertFalse(self.group_exists())
        resp = self.post_create_group()
        self.assertEqual(resp.status_code, 403)
        self.assertFalse(self.group_exists())

    def test_normal_user_cannot_create_group(self):
        self.assertFalse(self.group_exists())
        self.login(USERNAME, USERPASS)
        resp = self.post_create_group()
        self.assertFalse(self.group_exists())

    def test_admin_can_create_group(self):
        self.assertFalse(self.group_exists())
        self.login(ADMINNAME, ADMINPASS)
        resp = self.post_create_group()
        self.assertTrue(self.group_exists())

    def test_admin_cannot_create_unnamed_group(self):
        self.assertFalse(self.group_exists())
        self.login(ADMINNAME, ADMINPASS)
        resp = self.post_create_group(name='')
        self.assertFalse(self.group_exists())

        with self.assertRaises(Group.DoesNotExist):
            Group.get(name='')
