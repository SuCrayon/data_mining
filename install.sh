#!/bin/bash
os=`uname -o`

echo '===create a new python env==='
# create a new python env named "env"
python -m venv env
echo '===create env successfully==='

# activate the new env
if [ ${os} == 'Msys' ]
then
	source env/Scripts/activate
	echo 'Windows OS'
elif [ ${os} == 'GNU/Linux' ]
then
	source env/bin/activate
	echo 'Linux OS'
fi

echo '===start installing requirements==='
# install requirement
pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

echo 'successful'
