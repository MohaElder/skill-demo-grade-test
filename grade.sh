sudo apt-get update
sudo apt-get install python
mkdir student
mkdir student/chat-server
mkdir data
cp *.txt student/
cp chat-server/HandlerTests.java student/chat-server
cp chat-server/session.log student/chat-server
echo $1 > data/data.json
python3 skill-demo-manual-grade/skill_demo.py .