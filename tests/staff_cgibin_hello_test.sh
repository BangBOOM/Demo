cd ..
python3 webserv.py config.cfg &
PID=$!
cd -
curl localhost:8070/cgibin/hello.py | diff - hello_expected.out 
kill $PID
