import sys, os, cgi, urllib, re
from django.conf import settings

# form = cgi.FieldStorage()

class CASClient:

   def __init__(self):
      self.cas_url = 'https://fed.princeton.edu/cas/'

   def Authenticate(self, form):
      # If the request contains a login ticket, try to validate it
      if form.get('ticket'):
         netid = self.Validate(form['ticket'])
         if netid != None:
            return {"netid":netid}
         return {}
      # No valid ticket; redirect the browser to the login page to get one
      login_url = self.cas_url + 'login' \
         + '?service=' + urllib.quote(self.ServiceURL())
      # print 'Location: ' + login_url
      # print 'Status-line: HTTP/1.1 307 Temporary Redirect'
      # print ""
      return {"location":login_url}

   def Validate(self, ticket):
      val_url = self.cas_url + "validate" + \
         '?service=' + urllib.quote(self.ServiceURL()) + \
         '&ticket=' + urllib.quote(ticket)
      r = urllib.urlopen(val_url).readlines()   # returns 2 lines
      if len(r) == 2 and re.match("yes", r[0]) != None:
         return r[1].strip()
      return None
      # val_url = self.cas_url + "validate" + \
      #    '?service=' + urllib.parse.quote(self.ServiceURL()) + \
      #    '&ticket=' + urllib.parse.quote(ticket)
      # r = [x.decode('UTF-8') for x in urllib.request.urlopen(val_url).readlines()]   # returns 2 lines
      # if len(r) == 2 and re.match("yes", r[0]) != None:
      #    return str(r[1]).strip()
      # return None

   def ServiceURL(self):
      if os.environ.has_key('REQUEST_URI'):
         ret = 'http://' + os.environ['HTTP_HOST'] + os.environ['REQUEST_URI']
         ret = re.sub(r'ticket=[^&]*&?', '', ret)
         ret = re.sub(r'\?&?$|&$', '', ret)
         return ret
      elif settings.DEBUG == True:
         ret = "http://localhost:8000/login" 
         return ret
      # return "something is badly wrong"
      # if 'REQUEST_URI' in os.environ:
      #    ret = 'http://' + os.environ['HTTP_HOST'] + os.environ['REQUEST_URI']
      #    ret = re.sub(r'ticket=[^&]*&?', '', ret)
      #    ret = re.sub(r'\?&?$|&$', '', ret)
      #    return ret
      # elif settings.DEBUG == True:
      #    ret = "http://localhost:8000" + "/login"
      #    return ret
      # return "something is badly wrong"

def main():
  print "CASClient does not run standalone"

if __name__ == '__main__':
  main()