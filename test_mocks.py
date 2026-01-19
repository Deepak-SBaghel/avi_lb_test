from mocks import MockSSH, MockRDP

print("=== TESTING MOCK SSH ===")
MockSSH.connect("192.168.1.10", username="admin", password="pass")
output = MockSSH.execute_command("ls -la")
print("Command Output:", output)
MockSSH.disconnect()

print("\n=== TESTING MOCK RDP ===")
MockRDP.connect("192.168.1.20", username="administrator", password="pass")
MockRDP.execute_remote_action("open_browser", {"url": "https://google.com"})
MockRDP.disconnect()

if __name__ == "__main__":
    MockSSH.connect("localhost", username="root")
    MockSSH.execute_command("uptime")
    MockSSH.disconnect()

    MockRDP.connect("localhost", username="admin")
    MockRDP.execute_remote_action("test_action")
    MockRDP.disconnect()
