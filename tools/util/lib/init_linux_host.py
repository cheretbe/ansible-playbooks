import os
import sys
import json
import pathlib
import paramiko
import PyInquirer

def read_input(message, default_val, is_password=False):
    answers = PyInquirer.prompt(
        questions=[
            {
                "type": "password" if is_password else "input",
                "name": "value",
                "message": message,
                "default": "" if default_val is None else default_val
            }
        ]
    )
    if not answers:
        sys.exit(1)
    return answers["value"]

def exec_ssh_command(ssh_client, cmd):
    stdin, stdout, stderr = ssh_client.exec_command(
        cmd,
        get_pty=True
    )
    stdin.close()
    while True:
        line = stdout.readline()
        if not line:
            break
        print(line, end="")
    if stdout.channel.recv_exit_status() != 0:
        raise Exception(
            "SSH command returned non-zero exit status " +
            str(stdout.channel.recv_exit_status())
        )

def ssh_upload_file(sftp_client, src_file_path, dst_file_path):
    sftp_client.put(src_file_path, dst_file_path)

def main():
    config_file_name = os.path.expanduser("~/.cache/cheretbe/ansible-utils/host_init_cfg.json")
    if os.path.isfile(config_file_name):
        with open(config_file_name) as conf_f:
            config = json.load(conf_f)
    else:
        config = {}

    config["ssh_host"] = read_input("Host name", config.get("ssh_host"))
    config["ssh_username"] = read_input("SSH user name", config.get("ssh_username"))
    ssh_password = read_input("SSH password", "", is_password=True)
    config["ansible_user"] = read_input("Ansible user name", config.get("ansible_user"))
    config["ansible_public_key"] = read_input(
        "Ansible user public key file", config.get("ansible_public_key")
    )

    os.makedirs(os.path.dirname(config_file_name), exist_ok=True)
    with open(config_file_name, "w", encoding="utf-8") as conf_f:
        json.dump(config, conf_f, ensure_ascii=False, indent=4)

    ssh_client=paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(
        hostname=config["ssh_host"], username=config["ssh_username"], password=ssh_password
    )

    sftp_client = ssh_client.open_sftp()

    print("\nCreating temp directory")
    try:
        sftp_client.chdir("temp")
    except IOError:
        sftp_client.mkdir("temp", mode=0o770)
        sftp_client.chdir("temp")

    print("Uploading 'add_ansible_user.sh'")
    ssh_upload_file(
        sftp_client=sftp_client,
        src_file_path=pathlib.Path(__file__).resolve().parent / "add_ansible_user.sh",
        dst_file_path="add_ansible_user.sh"
    )
    sftp_client.chmod("add_ansible_user.sh", 0o770)

    print("Uploading public key file '{}' as 'ansible_user_key.pub'".format(
        config["ansible_public_key"]
    ))
    ssh_upload_file(
        sftp_client=sftp_client,
        src_file_path=config["ansible_public_key"],
        dst_file_path="ansible_user_key.pub"
    )

    print("Attempting to run 'add_ansible_user.sh' as root\n")
    temp_dir = sftp_client.getcwd()
    exec_ssh_command(
        ssh_client,
        "echo {ssh_password} | sudo -p '' -S bash -c '{temp_dir}/add_ansible_user.sh {ansible_user}'".format(
            ssh_password=ssh_password, temp_dir=temp_dir, ansible_user=config["ansible_user"]
        )
    )

    print("\nDeleting 'add_ansible_user.sh'")
    sftp_client.unlink("add_ansible_user.sh")
    print("Deleting 'ansible_user_key.pub'")
    sftp_client.unlink("ansible_user_key.pub")


if __name__ == "__main__":
    main()
