sudo apt-get update
sudo apt-get install python
mkdir students
mkdir data
cp *.txt students/
cp chat-server/HandlerTests.java students
cp chat-server/sesion.log students
echo $1 > data/data.json
python3 skill-demo-manual-grade/skill_demo.py .