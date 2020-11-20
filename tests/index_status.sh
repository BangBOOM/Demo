cd ..
python3 webserv.py config.cfg &
PID=$!
cd -
curl -I 127.0.0.1:8070/ 2> /dev/null | grep '200 OK' | diff - index_status.out 
kill $PID
