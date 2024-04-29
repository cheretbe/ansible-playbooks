# This script allows to read fingerprint of an SSH key with too broad
# permissions (happens when accessing Vagrant keys using Virtualbox
# shared folders on Windows hosts)
# The trick with echoing key file contents like this
#    echo /key/file | ssh-keygen -lf -
# doesn't work because it accepts only public keys. And we can't get the
# public key with -y option (read public key from private key file) since it
# also fails on too broad permissions.

# This script creates temporary copy of the file with correct permissions and
# makes sure the copy is deleted even if the scipt itself crashes.

if [ ! -e ${1} ]; then
  echo "_empty_"
  exit 0;
fi

key_value=$(<${1})

# -u, --dry-run: do not create anything; merely print a name
temp_key_file=$(mktemp -u)

# Use next available file descriptor
# https://www.gnu.org/software/bash/manual/html_node/Redirections.html
# Each redirection that may be preceded by a file descriptor number may instead
# be preceded by a word of the form {varname}. In this case, for each redirection
# operator except >&- and <&-, the shell will allocate a file descriptor greater
# than 10 and assign it to {varname}.
exec {temp_key_fd}<>${temp_key_file}

chmod 600 ${temp_key_file}

# The main trick is here.
# This is to make sure the file is deleted after use. Since it is open, the 
# descriptor is still available for the current process (and subprocesses). The
# filesystem entry will be deleted by the filesystem on close. Even if we don't
# close if explicitly, the kernel will do this automatically when the process
# exits (including kills and crashes)
rm ${temp_key_file}

echo "${key_value}" >&${temp_key_fd}
/usr/bin/ssh-keygen -yf /proc/$$/fd/${temp_key_fd}

# Close the file
eval "exec ${temp_key_fd}>&-"
