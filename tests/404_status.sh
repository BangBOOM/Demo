cd ..
python3 webserv.py config.cfg &
PID=$!
cd -
curl -I 127.0.0.1:8070/missing.html 2> /dev/null | grep '404' | diff - greetings_status_expected.out 
kill $PID
