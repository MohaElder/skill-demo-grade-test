sudo apt-get update
sudo apt-get install python
mkdir students
mkdir data
cp *.txt students/
touch data/data.json
cat $1 > data/data.json