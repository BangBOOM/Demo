cd ..
python3 webserv.py config.cfg &
PID=$!
cd -
curl localhost:8070/home.js | diff - js_expected.out 

\nkill \n
