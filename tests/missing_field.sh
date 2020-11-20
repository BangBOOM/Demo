cd ..
python3 webserv.py config.cfg &
PID=$!
cd -
python3 ../webserv.py broken_cfg.cfg | diff - missing_field.out
kill $PID
