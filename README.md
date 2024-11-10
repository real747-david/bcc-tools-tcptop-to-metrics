# bcc-tools-tcptop-to-metrics

这个是基于bcc tools中的tcptop脚本的输出转换为prometheus的metrics，并在grafana里查看的目的而生的。

tcptop的样例可以参考 https://github.com/iovisor/bcc/blob/master/tools/tcptop_example.txt

metrics类似这样， 分为发送和接收到的数据流量KB。包括进程pid，相应运行的用户或uid，local ip port，remote ip port，进程短命令行。
metrics只显示当前的流量top10的记录，如果想获取更多，请修改脚本中的top值。

# HELP tcp_rx_kb Bytes received over TCP connections
# TYPE tcp_rx_kb gauge
tcp_rx_kb{comm="b'nginx'",laddr="192.168.188.93:80",pid="4486",raddr="192.168.188.89:36600",user="nginx"} 0.0
tcp_rx_kb{comm="b'nginx'",laddr="192.168.188.93:80",pid="4486",raddr="192.168.188.89:49452",user="nginx"} 0.0
tcp_rx_kb{comm="b'nginx'",laddr="192.168.188.93:80",pid="4486",raddr="192.168.188.89:41000",user="nginx"} 0.0
tcp_rx_kb{comm="b'nginx'",laddr="192.168.188.93:80",pid="4486",raddr="192.168.188.89:33976",user="nginx"} 0.0
tcp_rx_kb{comm="b'nginx'",laddr="192.168.188.93:80",pid="4486",raddr="192.168.188.89:11944",user="nginx"} 0.0
tcp_rx_kb{comm="b'nginx'",laddr="192.168.188.93:80",pid="4486",raddr="192.168.188.89:37138",user="nginx"} 0.0
tcp_rx_kb{comm="b'python3'",laddr="192.168.188.93:8000",pid="28879",raddr="192.168.188.66:27518",user="root"} 0.0
tcp_rx_kb{comm="b'python3'",laddr="192.168.188.93:8000",pid="28879",raddr="192.168.188.66:27320",user="root"} 0.0
tcp_rx_kb{comm="b'python3'",laddr="192.168.188.93:8000",pid="28879",raddr="192.168.188.66:27386",user="root"} 0.0
tcp_rx_kb{comm="b'python3'",laddr="192.168.188.93:8000",pid="28879",raddr="192.168.188.66:27452",user="root"} 0.0
# HELP tcp_tx_kb Bytes sent over TCP connections
# TYPE tcp_tx_kb gauge
tcp_tx_kb{comm="b'nginx'",laddr="192.168.188.93:80",pid="4486",raddr="192.168.188.89:36600",user="nginx"} 6.0
tcp_tx_kb{comm="b'nginx'",laddr="192.168.188.93:80",pid="4486",raddr="192.168.188.89:49452",user="nginx"} 6.0
tcp_tx_kb{comm="b'nginx'",laddr="192.168.188.93:80",pid="4486",raddr="192.168.188.89:41000",user="nginx"} 6.0
tcp_tx_kb{comm="b'nginx'",laddr="192.168.188.93:80",pid="4486",raddr="192.168.188.89:33976",user="nginx"} 6.0
tcp_tx_kb{comm="b'nginx'",laddr="192.168.188.93:80",pid="4486",raddr="192.168.188.89:11944",user="nginx"} 6.0
tcp_tx_kb{comm="b'nginx'",laddr="192.168.188.93:80",pid="4486",raddr="192.168.188.89:37138",user="nginx"} 6.0
tcp_tx_kb{comm="b'python3'",laddr="192.168.188.93:8000",pid="28879",raddr="192.168.188.66:27518",user="root"} 0.0
tcp_tx_kb{comm="b'python3'",laddr="192.168.188.93:8000",pid="28879",raddr="192.168.188.66:27320",user="root"} 0.0
tcp_tx_kb{comm="b'python3'",laddr="192.168.188.93:8000",pid="28879",raddr="192.168.188.66:27386",user="root"} 0.0
tcp_tx_kb{comm="b'python3'",laddr="192.168.188.93:8000",pid="28879",raddr="192.168.188.66:27452",user="root"} 0.0

如何使用：
1，kernel需要支持ebpf的特性，目测测试系统rhel8.9和rhel9.3没啥问题。

2，安装bcc-tools，安装镜像里就有这个包 yum -y install bcc-tools
[root@rhel93 ~]# rpm -qa |grep bcc-tools
bcc-tools-0.26.0-4.el9.x86_64

3，安装python3的pip包，yum -y install python3-pip.noarch

4，安装python3里面的prometheus_client包， python3 -m pip install prometheus_client

5，下载脚本，运行 python3 tcptop-metrics.py 

metrics的web默认监听8000端口，更改端口需要修改代码里的端口相关的配置即可。

prometheus的配置：

  - job_name: "tcptop"
    static_configs:
      - targets:
          - "192.168.188.89:8000"
          - "192.168.188.93:8000"
       
grafana dashboard 请下载文件 ebpf TCP top10-1731217974976.json
