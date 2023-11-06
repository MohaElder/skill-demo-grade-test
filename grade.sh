sudo apt-get update
sudo apt-get install python
mkdir students
mkdir students/chat-server
mkdir data
cp *.txt students/
cp chat-server/HandlerTests.java students/chat-server
cp chat-server/sesion.log students/chat-server
echo $1 > data/data.json
python3 skill-demo-manual-grade/skill_demo.py .