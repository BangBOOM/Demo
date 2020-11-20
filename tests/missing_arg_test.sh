cd ..
python3 webserv.py config.cfg &
PID=$!
cd -
python3 ../webserv.py | diff - missing_arg.out
kill $PID
