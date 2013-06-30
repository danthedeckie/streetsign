import models

models.create_all()

d = models.User(loginname='daniel',displayname='daniel',
                emailaddress='d@rsdt.org')

d.set_password('12345')

d.is_admin = True

h = models.User(loginname='henrik',displayname='Henrik',
                emailaddress='henrik.weber@om.org')

h.set_password('password')

d.save()
h.save()

p = models.Post()
pp = models.Post()

f = models.Feed()

f.grant('Read',h)
