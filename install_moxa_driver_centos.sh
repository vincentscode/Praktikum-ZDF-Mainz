echo "Running CentOS Moxa Driver Installer 0.0.1"

# root check
if [ "$EUID" -ne 0 ]
	then echo "Please run as root"
	exit
fi

# download the driver into /tmpt/moxa/
echo "Downloading the moxa driver..."
cd /tmp/
wget https://bit.ly/36QZKL0
file 36QZKL0
mv 36QZKL0 moxa.tgz
tar zxvf moxa.tgz
cd moxa/

# print the kernel version
echo "Kernel Version:"
uname -a
uname -r

# update all packages
echo "Updating Packages..."
yum check-update
yum update

# install the driver requirements
echo "Installing required Packages..."
yum install -y make
yum install -y gcc
yum install -y ld
yum install -y libc
yum install -y binutils
yum install -y gunzip
yum install -y gawk
yum install -y openssl
yum install -y libssl-dev
yum install -y libssl
yum install -y elfutils-libelf-devel
yum install -y openssl-devel

# check if kernel headers are installed
echo "Currently installed Kernel Headers:"
cd /usr/src/kernels/
ls -l

read -r -p "Install Kernel Headers? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
	# install kernel headers
	echo "Installing Kernel Headers..."
	yum install -y kernel-devel
	yum install -y kernel-headers

	echo "Installed Kernel Headers:"
	cd /usr/src/kernels/
	ls -l
fi

echo "Current Kernel Headers Installed"
ls -l /usr/src/kernels/$(uname -r)
read -r -p "Move Kernel Header? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
	mv /usr/src/kernels/? /usr/src/kernels/$(uname -r)
	ls -l /usr/src/kernels/$(uname -r)
fi

# ./mxinst
read -rsp $"Press any key to install the driver (runs './mxinst')\n" -n 1 key
echo "Installing..."

status=$?
cmd="./mxinst"
$cmd
status=$?
if [ $status -eq 0 ]
then
	echo "Installed successfully"
	exit
fi


read -r -p "Disable Module Validation (runs 'mokutil --disable-validation')? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
	echo "Disabling Module Validation..."
	yum install -y mokutil
	mokutil --disable-validation
fi