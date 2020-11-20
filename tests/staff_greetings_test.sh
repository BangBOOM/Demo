cd ..
python3 webserv.py config.cfg &
PID=$!
cd -
curl localhost:8070/greetings.html | diff - greetings_expected.out 
kill $PID
