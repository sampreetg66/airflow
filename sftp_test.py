import pysftp

# Define the SFTP server details
hostname = 'your.sftp.server'
username = 'your_username'
password = 'your_password'
port = 22  # Default SFTP port is 22

# Optional: Define a known_hosts file to avoid host key verification
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None  # Disable host key checking

try:
    # Establish the SFTP connection
    with pysftp.Connection(host=hostname, username=username, password=password, port=port, cnopts=cnopts) as sftp:
        print("Connection successfully established!")
        
        # List files in the remote directory
        remote_path = '/remote/directory/path'
        files = sftp.listdir(remote_path)
        print(f"Files in {remote_path}:")
        for file in files:
            print(file)
            
except Exception as e:
    print(f"An error occurred: {e}")
