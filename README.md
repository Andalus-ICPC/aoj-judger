# Andalus JUdge Server Installation Guide

This is a brief guide on how to install the Andalus Judge Server on your machine.

Before any installation make sure you have the latest version of Python 3 installed on your machine and the path is configured properly, also since we are using a virtual environment make sure you you have virtual environment of your choice.

But if you don't have a virtual environment install it using the following command first.

Mainly the OS on your machine should be a linux based OS. This means all the following commands are not guaranteed to work on Windows machine.

```sh
pip install virtualenv
```

#### Step 1: Install compilers on the machine:

Install compilers for Python3, Python2, C++, C and Java on the machine.

Install Python3 version 3.6.9
```sh
sudo apt-get install python3
```


Install Python2 version 2.7.15
```sh
sudo apt-get install python2
```


Install g++ version 7.5.0
```sh
sudo apt-get install g++
```


Install gcc version 7.5.0
```sh
sudo apt-get install gcc
```

Install Java version 11.0.11
```sh
sudo apt-get install openjdk-11-jdk-headless
```


#### Step 2: Create a folder that will contain everything, then go into the folder :file_folder:

#### Step 3: Now pull the necessary files from github :arrow_double_down:

The following clones the judger
```sh
git clone https://github.com/Andalus-ICPC/aoj-judger.git
```

The following clones the sandbox
```sh
git clone https://github.com/Andalus-ICPC/SandboxCommandRunner.git
```

#### Step 4: Now let's get to them one by one

- For the judger

```sh
cd aoj-judger
```

Now create a virtual environment
```sh
python -m virtualenv env
```
But if you are on linux and you are getting an error, try the following command
```sh
python3 -m virtualenv env
```
This will create a vritual environment named `env` inside `aoj-judger`

Activate the virtual environment
For linux
```sh
source /env/bin/activate
```

Then install all the requirements
```sh
pip install -r requirements.txt
```
But if you are on linux and you are getting an error, try the following command
```sh
pip3 install -r requirements.txt
```

- For the sandbox

```sh
cd SandboxCommandRunner
```

Here we don't need any virtual environment, we just execute the following commands.

```sh
sudo apt-get install libseccomp-dev
```

```sh
mkdir build && cd build && cmake .. && make && sudo make install && cd ..
```

```sh
sudo python3 bindings/python/setup.py install
```

#### Step 5: We are almost there, just a few configurations left :tired_face:

- Now go to `aoj-judger` and setup where and how to run one script

Inside the `start-and-run-flask` folder, you will get 1 file, `flask_run`

```
source /home/andalus/Documents/django/Andalus-Judge-Repo/aoj-judger/env/bin/activate && cd /home/andalus/Documents/django/Andalus-Judge-Repo/aoj-judger && export FLASK_APP=/home/andalus/Documents/django/Andalus-Judge-Repo/aoj-judger/server.py && flask run -h 0 -p 5000

# run as root
```

**Change** `/home/andalus/Documents/django/Andalus-Judge-Repo/aoj-judger/` to the path where your `aoj-judger` lives.

##### Step 6: Finally run everything :thumbsup: :rocket:

```sh
cd aoj-judger/start-and-run-flask
```

```sh
sudo su
```

After you enter your credentials

```sh
bash flask_run
```
