PIDS=`lsof -i:9009|grep LISTEN|awk '{print $2}'`
echo $PIDS
for pid in $PIDS
do
kill -9 $pid
echo "kill $pid"
done
echo 'end'
nohup python termmain.py &
