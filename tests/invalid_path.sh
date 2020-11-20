cd ..
python3 webserv.py config.cfg &
PID=$!
cd -
python3 ../webserv.py invalid | diff - invalid_path.out
kill $PID
