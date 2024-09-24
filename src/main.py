import psutil
import time
import threading

class ProcessManager:
    def __init__(self):
        self.process_name:str = "maestro"
        self.running = True
        self.seen_pids = set() 

    def find_processes_by_name(self):
        """주어진 이름을 가진 모든 프로세스 검색"""
        return {proc.info['pid'] for proc in psutil.process_iter(['pid', 'name']) 
                if self.process_name.lower() in proc.info['name'].lower()}

    def terminate_processes(self, pids):
        """주어진 PIDs를 가진 프로세스 종료"""
        for pid in pids:
            try:
                psutil.Process(pid).terminate()
                print(f"Process {pid} terminated.")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass  # 무시

    def monitor_processes(self):
        """지속적으로 프로세스를 모니터링하여 특정 프로세스를 종료"""
        while self.running:
            current_pids = self.find_processes_by_name()
            new_pids = current_pids - self.seen_pids  # 새로 발견된 PID

            if new_pids:
                print(f"Found new processes '{self.process_name}' with PIDs: {new_pids}. Terminating...")
                self.terminate_processes(new_pids)

            self.seen_pids.update(current_pids)  # 확인한 PID를 업데이트
            time.sleep(10)  # CPU 사용량을 줄이기 위해 잠시 대기

if __name__ == "__main__":
    pm = ProcessManager()

    # 모니터링을 별도의 스레드에서 실행
    monitoring_thread = threading.Thread(target=pm.monitor_processes)
    monitoring_thread.start()

    print("Monitoring started... Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1) 
    except KeyboardInterrupt:
        pm.running = False
        monitoring_thread.join()
        print("Monitoring stopped.")
