import socket
import numpy as np

# UDP settings
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 4242       # SmoothTrack’s configured port

# Initialize UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((HOST, PORT))

def decode_6dof_data(data):
    """Decode 48 bytes of 6DOF head tracking data from SmoothTrack."""
    if len(data) != 48:
        print(f"Warning: Received {len(data)} bytes, expected 48.")
        return None
    
    values = np.frombuffer(data, dtype=np.float64)
    return {
        'X': values[0],
        'Y': values[1],
        'Z': values[2],
        'Yaw': values[3],
        'Pitch': values[4],
        'Roll': values[5]
    }

def main():
    print(f"Listening for 6DOF head tracking data on {HOST}:{PORT}...")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            # Receive UDP data
            data, addr = udp_socket.recvfrom(1024)
            tracking_data = decode_6dof_data(data)
            
            if tracking_data:
                print(f"From {addr}:")
                for key, value in tracking_data.items():
                    print(f"  {key}: {value:.2f}")
                print("-" * 30)
    
    except KeyboardInterrupt:
        print("\nStopped by user.")
    
    finally:
        udp_socket.close()
        print("Socket closed.")

if __name__ == "__main__":
    main()