curl -i -H "Content-Type: application/json" -X GET http://localhost:5000/start

curl -i -H "Content-Type: application/json" -X POST -d '{"src_ip":"192.168.0.134","dow":"0,1,2,3,4","time_start":"18:00","time_end":"23:59","dst_str":"*.youtube.com","action":"block"}' http://localhost:5000/saverule
curl -i -H "Content-Type: application/json" -X POST -d '{"src_ip":"127.0.0.1","dow":"0,1,2,3,4","time_start":"18:00","time_end":"23:59","dst_str":"*.youtube.com","action":"block"}' http://localhost:5000/saverule
curl -i -H "Content-Type: application/json" -X GET http://localhost:5000/get/rules

host www.youtube.com localhost

