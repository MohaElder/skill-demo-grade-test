import json
import os
import re
import sys

# skill_demo2: To test, use
#   python skill_demo.py sample/workspace
# (and replace the argument with your test data if you like)
if len(sys.argv) <= 1:
  gradebase = "/grade/"
else:
  gradebase = sys.argv[1]

query = os.path.join(gradebase, "student", "query-output.txt")
root = os.path.join(gradebase, "student", "root-output.txt")
testfail = os.path.join(gradebase, "student", "test-fail-output.txt")
testsuccess = os.path.join(gradebase, "student", "test-success-output.txt")
testnew = os.path.join(gradebase, "student", "new-test-output.txt")
session = os.path.join(gradebase, "student", "chat-server", "session.log")
handlertests = os.path.join(gradebase, "student", "chat-server", "HandlerTests.java")

testfailexpect = """
JUnit version 4.13.2
...
Time: IGNORE
There was 1 failure:
1) handleRequest2(HandlerTests)
org.junit.ComparisonFailure: expected:<[edwin: happy friday!

]> but was:<[Invalid parameters: name=edwin&message=happy friday!]>
	at org.junit.Assert.assertEquals(Assert.java:117)
	at org.junit.Assert.assertEquals(Assert.java:146)
	at HandlerTests.handleRequest2(HandlerTests.java:22)

FAILURES!!!
Tests run: 3,  Failures: 1
"""

testsuccessexpect = """
JUnit version 4.13.2
...
Time: IGNORE

OK (3 tests)
"""

with open(os.path.join(gradebase, "data/data.json"), "r") as read_file:
    data = json.load(read_file)

# NOTE(joe): the JUnit output has a line that says “Time: ...”, we need to
# ignore that since time may not be the same.
# Also, JUnit is not guaranteed to run tests in the same order, so the ..E.
# line could have the E anywhere, so strip that as well and always show ...
# The (single) failure is always consistent, so that's really what we're
# comparing
def junit_clean(output):
  output = output.strip()
  output = re.sub(r"Time: .*", "Time: IGNORE", output)
  output = re.sub(r"^\..*", "...", output, flags=re.MULTILINE)
  output = re.sub(r"\s+", " ", output)
  return output

def grade_tests(file, expect):
  with open(file) as f:
    txt = f.read()
    txt = junit_clean(txt)
  expect = junit_clean(expect)
  return (txt.strip() == expect.strip(), txt, expect)

(testfailcorrect, _, _) = grade_tests(testfail, testfailexpect)
(testsuccesscorrect, _, _) = grade_tests(testsuccess, testsuccessexpect)

def grade_query(file, data):
  expect = f"{data['params']['user']}: {data['params']['message']}"
  with open(file) as f: txt = f.read()
  return (txt.strip() == expect.strip(), txt, expect)

(querycorrect, _, _) = grade_query(query, data)

def grade_root(file, data):
  expect = f"""
{data['params']['user2']}: {data['params']['message2']}

{data['params']['user']}: {data['params']['message']}
"""
  with open(file) as f: txt = f.read()
  return (txt.strip() == expect.strip(), txt, expect)

(rootcorrect, _, _) = grade_root(root, data)

def check_server_paths(logfile):
  with open(logfile) as f: logtext = f.read() 
  lines = logtext.split("\n")
  hasroot = False
  chatcount = 0
  hasuser = False
  hasmessage = False
  hasuser2 = False
  hasmessage2 = False

  for l in lines:
    if l.strip() == "/": hasroot = True
    if l.startswith("/chat"): chatcount += 1
    if data['params']['user'] in l: hasuser = True
    if data['params']['message'] in l: hasmessage = True
    if data['params']['user2'] in l: hasuser2 = True
    if data['params']['message2'] in l: hasmessage2 = True

  enoughchats = False
  if chatcount >= 3: enoughchats = True

  hasparams = hasuser and hasmessage and hasuser2 and hasmessage2

  return (hasroot, enoughchats, hasparams)

(hasroot, enoughchats, hasparams) = check_server_paths(session)


testnewexpect = """
JUnit version 4.13.2
...
Time: IGNORE

OK (4 tests)
"""

def check_junit_test(javafile):
  with open(javafile) as j: javatext = j.read()
  # Should be 4 tests
  numtests = len(javatext.split("@Test"))
  # Should be 6 or more handleRequests
  numrequest = len(javatext.split("handleRequest"))
  # Should be 4 or more assertEquals
  numasserts = len(javatext.split("assertEquals"))

  hasroot = ("\"/\"" in javatext) or ("localhost:4000/\"" in javatext) or ("localhost:4000\"" in javatext)

  (newtestcorrect, _, _) = grade_tests(testnew, testnewexpect)

  return (numtests >= 4, numrequest >= 6, numasserts >= 4, hasroot, newtestcorrect)

(hastests, hasrequests, hasasserts, hasroottest, newtestcorrect) = check_junit_test(handlertests)

score = 0
max_score = 6
details = ""

if testfailcorrect: score += 1
else: details += "Incomplete: test-fail-output.txt did not have the expected output\n"

if testsuccesscorrect: score += 1
else: details += "Incomplete: test-success-output.txt did not have the expected output\n"

if querycorrect: score += 1
else: details += "Incomplete: query-output.txt did not have the expected output\n"

if rootcorrect: score += 1
else: details += "Incomplete: root-output.txt did not have the expected output\n"

if hasroot and enoughchats and hasparams: score += 1
else:
  if not enoughchats: details += "Incomplete: did not see requests for multiple /chat queries\n"
  if not hasparams: details += "Incomplete: did not see all parameters in /chat queries\n"
  if not hasroot: details += "Incomplete: did not see a request for the root path\n"

hasnewtest = False
if hastests and hasrequests and hasasserts and hasroottest and newtestcorrect:
  hasnewtest = True
  score += 1
else:
  if not hastests: details += "Incomplete: did not see a 4th JUnit test\n"
  if not hasrequests: details += "Incomplete: did not see additional uses of handleRequest in JUnit tests\n"
  if not hasasserts: details += "Incomplete: did not see additional uses of assertEquals in JUnit tests\n"
  if not hasroottest: details += "Incomplete: did not see use of the root path \"/\" in JUnit tests\n"
  if not newtestcorrect: details += "Incomplete: new-test-output.txt did not have the expected output\n"


message = f"""
There are 6 possible 'points' corresponding to the different parts of the
skill demonstration.

Your score is {score}/{max_score}

You are free to use the output below to try again after you submit. If you get
the message "All checks passed" there is no more for you to do, you've
completed all the steps.
"""

if score == 6: message += "\nAll checks passed"
if score <= 5: message += "\nMissing some steps detailed below:\n\n" + details

results = {
  'message': message,
  'score': score/max_score,
  'testfail': testfailcorrect,
  'testsuccess': testsuccesscorrect,
  'query': querycorrect,
  'root': rootcorrect,
  'hasroot': hasroot,
  'enougchats': enoughchats,
  'hasnewtest': hasnewtest
}

print(json.dumps(results))
