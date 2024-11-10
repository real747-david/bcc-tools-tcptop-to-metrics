import subprocess
import time
from prometheus_client import start_http_server, Gauge
import re
from collections import deque
import pwd  # 用于将 UID 转换为用户名

# Prometheus metrics
tcp_rx_kb = Gauge('tcp_rx_kb', 'Bytes received over TCP connections', ['pid', 'user', 'laddr', 'raddr', 'comm'])
tcp_tx_kb = Gauge('tcp_tx_kb', 'Bytes sent over TCP connections', ['pid', 'user', 'laddr', 'raddr', 'comm'])

def is_tcptop_running(process):
    return process and process.poll() is None

def start_tcptop():
    process = subprocess.Popen(['/usr/share/bcc/tools/tcptop'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Debug: Started tcptop with PID {process.pid}")
    return process

def run_tcptop():
    process = start_tcptop()
    
    while True:
        if not is_tcptop_running(process):
            print("Debug: tcptop is not running. Restarting...")
            process = start_tcptop()
        
        output = process.stdout.readline()
        if output:
            yield output.decode('utf-8').strip()

def parse_output(line):
    # Parse the tcptop output line to extract metrics
    match = re.match(r'(\d+)\s+(\S+)\s+([\d\.]+:\d+)\s+([\d\.]+:\d+)\s+(\d+)\s+(\d+)', line)
    if match:
        pid = match.group(1)
        comm = match.group(2)
        laddr = match.group(3)
        raddr = match.group(4)
        rx_kb = int(match.group(5))
        tx_kb = int(match.group(6))
        
        # 获取用户名
        try:
            with open(f'/proc/{pid}/status', 'r') as f:
                for line in f:
                    if line.startswith('Uid:'):
                        uid = int(line.split()[1])
                        try:
                            user = pwd.getpwuid(uid).pw_name
                        except KeyError:
                            user = str(uid)
                        break
        except FileNotFoundError:
            user = "unknown"
        
        return pid, user, laddr, raddr, comm, rx_kb, tx_kb
    return None

def update_metrics():
    rx_metrics = deque(maxlen=10)
    tx_metrics = deque(maxlen=10)
    
    while True:
        for line in run_tcptop():
            metrics = parse_output(line)
            if metrics:
                pid, user, laddr, raddr, comm, rx_kb, tx_kb = metrics
                
                # Update deque directly
                rx_metrics.append((rx_kb, pid, user, laddr, raddr, comm))
                tx_metrics.append((tx_kb, pid, user, laddr, raddr, comm))
                
                # Sort and get top 10
                top_rx_metrics = sorted(rx_metrics, key=lambda x: x[0], reverse=True)[:10]
                top_tx_metrics = sorted(tx_metrics, key=lambda x: x[0], reverse=True)[:10]

                # Update Prometheus metrics
                tcp_rx_kb.clear()
                tcp_tx_kb.clear()
                
                for rx_kb, pid, user, laddr, raddr, comm in top_rx_metrics:
                    tcp_rx_kb.labels(pid=pid, user=user, laddr=laddr, raddr=raddr, comm=comm).set(rx_kb)
                
                for tx_kb, pid, user, laddr, raddr, comm in top_tx_metrics:
                    tcp_tx_kb.labels(pid=pid, user=user, laddr=laddr, raddr=raddr, comm=comm).set(tx_kb)

                # Debug output
                print(f"Debug: tcptop line - {line}")
                print(f"Debug: Top RX Metrics: {top_rx_metrics}")
                print(f"Debug: Top TX Metrics: {top_tx_metrics}")

        time.sleep(0.5)  # This can dynamically be adjusted based on conditions


if __name__ == '__main__':
    start_http_server(8000)
    print("Prometheus server started on port 8000")
    update_metrics()