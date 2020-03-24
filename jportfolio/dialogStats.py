#!/mesonet/python/bin/python
# Script to extract dialog Stats from the dialog
# Daryl Herzmann  19 Sept 2002
# 14 Apr 2004 	Lets make this a bit nicer

import pg
mydb = pg.connect('portfolio', 'meteor.geol.iastate.edu', 5432)
_ETHICAL = "13674"
_P01 = "13566"
_P15 = "13722"
_EDATE = '2005-04-30'


rs = mydb.query("SELECT u.* from users u, students s \
   WHERE s.portfolio = 'gcp2005' \
   and s.username = u.username").dictresult()

for i in range(len(rs)):
  user = rs[i]["username"]

   # Retrieve a count of postings
  q1 = "SELECT count(username) as count, \
    round(avg(length(body)),1) as length \
    from dialog WHERE username = '"+ user +"' and security = 'public' and \
    portfolio = 'gcp2005' and \
    threadid >= "+_P01+" and threadid != "+ _ETHICAL +" \
    and threadid <= "+_P15+" and date(date) < '"+_EDATE+"'"
  rs1 = mydb.query(q1).dictresult()
  posts = rs1[0]["count"]
  avglen = rs1[0]["length"]

  rs2 = mydb.query("SELECT to_char(idnum, '999999999999999999999999999999999999') as idnum from dialog WHERE username = '"+ user +"' \
    and portfolio = 'gcp2005' and security = 'public' \
    and threadid >= "+_P01+" and threadid <= "+_P15+" \
    and threadid != "+_ETHICAL+" \
    and date(date) < '"+_EDATE+"'").dictresult()

    # Loop over all entries made by user into the database
  totalReplies = 0
  myposts = {}
  for j in range(len(rs2)):
    thisid = rs2[j]["idnum"]
    myposts[str(thisid)] = 1
    sqlf = "SELECT count(username) as count from dialog \
      WHERE security = 'public' and portfolio = 'gcp2005' \
      and username != '%s' \
      and idnum BETWEEN (%s::numeric * 10000)::numeric \
      AND ( (%s::numeric + 1)* 10000)::numeric "
    sql = sqlf % (user, thisid, thisid)
    rs3 = mydb.query(sql).dictresult()
    totalReplies = totalReplies + int(rs3[0]["count"])

    # Pull in the number of responses this author did
  rs4 = mydb.query("SELECT to_char(idnum, '999999999999999999999999999999999999') as idnum from dialog \
    WHERE portfolio = 'gcp2005' \
    and username = '"+ user +"' and idnum > 1000000000000::numeric \
    and security = 'public' and \
    threadid >= "+_P01+" and threadid <= "+_P15+" \
    and threadid != "+_ETHICAL+" \
    and date(date) < '"+_EDATE+"'").dictresult()
  selfReplies = 0
  for q in range(len(rs4)):
    thisid = str(rs4[q]["idnum"])
    parentPost = "    "+ thisid[:-4]
    if (myposts.has_key(parentPost)):
      hi = 'hi'
      #print "%s,%s" % (parentPost, thisid)
    else:
      selfReplies += 1

  print "%s, %s, %s, %s, %s, %s, %s" % (user, rs[i]["fname"], rs[i]["lname"], posts, totalReplies, selfReplies, avglen) 
