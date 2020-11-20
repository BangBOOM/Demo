cd ..
python3 webserv.py config.cfg &
PID=$!
cd -

for t in *.sh;
do
	bash $t
done;
