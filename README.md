# Stroke Rehabilitation Coaching Robot

This branch contains code for running the stroke rehabilitation system on Pepper. This README is written with the intention to allow people from Heriot-Watt University and the National Robotarium to run the system as demonstrations. If you are external to this group, please see the master branch to get things up and running and start editing the code for your application.

Below are specific instructions for installing and running the demonstration.

The demonstration uses the same code as was used for the short-term evaluation of the system with participants so should be fairly robust. However, it is a bit complex to set up and run and the code is a bit hacked together in places. A description of the studies run and the background to the project can be found in the demos folder in Dropbox: https://www.dropbox.com/home/ITT%20Group%20team%20folder/Demos/Squash%20and%20Stroke%20Rehabilitation.

NOTE: The stroke rehabilitation demo does not include the capacity for low-level adaption using reinforcement learning. This is only implemented in the squash coaching system.

NOTE: The demonstration will only work on the ITT group's Pepper (the one with the "EM1.69" sticker on the back) due to different tablet versions on the other Peppers. They are set up to work with the ITT Pepper router at the moment. If you wish to run the demos through a different network, you will have to update the IP address in config.py, and in the various other components.
  
## Instructions for Installing and Running (applicable to both squash and rehabilitation)
  ### Requirements
  1. Ubuntu 16.04 (newer versions might work but I had problems with any version other than this).
     
     a) You can install Ubuntu alongside Windows (dual-boot) by following the instructions here: https://itsfoss.com/install-ubuntu-1404-dual-boot-mode-windows-8-81-uefi/
     
     b) I found that it wasn't necessary to conduct "Step 4: Make some free space on your disk for Ubuntu installation" because the Ubuntu installer will partition your hard drive automatically during installation.
  2. Python 2 and Python 3 (not great practice I know, but some parts of the Naoqi SDK only work with Python 2 and some other functionality was a lot easier to implement in Python 3).
      
      a) Python 2 should already be installed with Ubuntu 16.04. You can check which version you have by typing ```python -V``` into a terminal window.
      
      b) Python 3.5 may also be installed with Ubuntu 16.04. However, PyCharm has removed support of Python 3.5, so we need a newer version. Installing newer versions of Python is slightly more complicated in 16.04 than in newer versions of Ubuntu, but you can do it using the following commands in a terminal window:
      
         sudo apt-get install aptitude
         sudo aptitude install python3.8
      
      c) You can verify the installation was successful by typing ```python3.8 -V``` into a terminal window.
  3. Pycharm v2020.3
    <Instructions on downloading and installing Pycharm>
    
      a) Visit https://www.jetbrains.com/pycharm/download/other.html and scroll down to v2020.3. The demos might work with newer versions of PyCharm but I haven't tested it.
      
      b) Extract the contents of the tar file to the location of your choice.
      
      c) Run Pycharm by opening a terminal, navigating to {extract_location}/bin, and typing ```./pycharm.sh```.
      
  5. Choregraphe v2.5.10.7
    <Instructions on downloading and installing Choregraphe>
      
      a) The version of Choregraphe you install will depend on the version of the Naoqi operating system that is installed on the particular Pepper robot you are using. For the ITT Pepper robot, we want version 2.5.10.7, which can be downloaded via the Heriot-Watt internal Dropbox: https://www.dropbox.com/home/ITT%20Group%20team%20folder/Choregraphe/Alternative/Version%202.5.
      
      b) Download and run the Linux file: choregraphe-suite-2.5.10.7-linux64-setup.run. You may need to adjust the permissions of the file to allow it to be executed: right click the downloaded file and select Permissions, and on the permissions tab check the box labelled "Allow executing file as program". Then open the folder in a terminal window and execute ```./choregraphe-suite-2.5.10.7-linux64-setup.run```
      
      c) Follow the installation wizard to install Choregraphe.
      
      d) Enter the license key when prompted, which can be found in the licensekey.txt file on Dropbox: https://www.dropbox.com/home/ITT%20Group%20team%20folder/Choregraphe/Alternative?preview=license+key.txt
  ### Downloading components
  The demonstration is split into multiple different components which communicate through API's. The following are all of the dmoain independent components:
  #### 1. Robotic Exercise Coach - Pepper
  This is the current repo and is where the main program is stored. It does everything to do with the policies, deciding what action to take, RL to adapt the policies, behaviour tree to track the place within the session etc. Written in Python 3.
      
  Once you have installed Pycharm, as above, clone this repo into Pycharm as a new project:
  
  a) Open Pycharm.
     
  b) Upon running, you can import a project from version control (e.g. this project or one of the others listed below):
      
  (i) Select "Get from VCS" on the welcome screen.
      
  (ii) You will also need to install git by typing ```sudo apt install git``` in a terminal window. This may not install the required git version, so you might still see an error message in PyCharm. If this happens you can install the latest version of git as follows:
      
      sudo add-apt-repository ppa:git-core/ppa
      sudo apt update
      sudo apt install git
      
  c) Next, enter the URL of the repository you want to download (e.g. https://github.com/M4rtinR/coachingPolicies.git) and click "clone". You should fork the project first into your own repository if you plan to edit the code.
      
  d) You may need to click "Trust project" before it will open in PyCharm.
  
  You should now be able to select the "long-term stroke" branch in PyCharm.
  #### 2. Robot Interface for Robotic Exercise Coach: https://github.com/M4rtinR/Robot-Interface-for-Robotic-Exercise-Coach
  This is where the interaction with the user is done through Pepper. All of the actions are sent here to be conducted by Pepper and any use of Pepper's touch sensors/limbs is dealt with here. Written in Python 2.
      
  Similar to component 1 above, clone the robot test repo into a new Pycharm project. You should then be able to select the required branch for the particular demo you wish to run. For detailed instructions, see the README in the repo.
  #### 3. Screen Interface for Robotic Exercise Coach: https://github.com/M4rtinR/Screen-Interface-for-Robotic-Exercise-Coach
  This is where the display on Pepper's tablet computer screen and interaction with the screen from the user is handled. Written in Python 3.
      
  For this component you will need to run Pycharm as an administrator. In a terminal, open the folder in which Pycharm is installed (for me this is /snap/pycharm-community/current/bin) and use the following command:
  ```sudo ./pycharm.sh```
  and enter your password when prompted. Now clone the rehab interface repo into your admin-run Pycharm as above and you should be able to select the required branch for the particular demo you wish to run. For detailed instructions, see the README in the repo.
  
  ### Domain-Dependent Components   
  #### 2. Operator Input for Robotic Exercise Coach: https://github.com/M4rtinR/Operator-Input-for-Robotic-Exercise-Coach (Stroke Rehabilitation only)
  This branch contains the code for the stroke rehabilitation system, so an additional component is needed. The operator input replaces any sensing software used in the squash system, and allows the operator to signal completion of each exercise repitition to the robot. Written in Python 3.
  
## Running the Demo
   Now that you have all of the components downloaded on your machine, conduct the following steps to run the squash demo on Pepper:
      
   1. Set the Python Interpreter.
   
      a) In PyCharm, go to File -> Settings -> Project: coachingPolicies -> Python Interpreter
      
      b) Click "Add Interpreter".
      
      c) In the popup window, select Python 3.8 that you installed earlier.
      
   2. Setup run configurations.
   
      a) In the project explorer window on the left, expand coachingBehaviourTree and right click controller.py to select "Modify run configurations".
      
      b) It should auto-populate most fields and show Python 3.8 as the interpreter.
      
      c) Click "OK" to apply this configuration.
      
   3. Install the required libraries.
   
      a) The first library to install is required to run the behaviour tree (https://github.com/ToyotaResearchInstitute/task_behavior_engine).
      
      (i) It can be installed by entering the following commands in a terminal window:
      
          sudo apt-get update -y
          sudo apt-get install -y \
              cmake \
              git \
              python-catkin-pkg
          git clone https://github.com/ToyotaResearchInstitute/task_behavior_engine.git
          cd task_behavior_engine
          sudo python setup.py install
       (ii) Next, add the newly installed library as a source folder to your project. Go to File -> Settings -> Project Structure. Click "Add Content Route" and point to <install folder>/task_behaviour_engine/src. Click the src folder and select "Mark as: Sources" at the top of the window. You will need to do this in each branch you want to use the code from.
       
       b) To install the below packages, you should be able to do it through the GUI of PyCharm. Go to File -> Settings -> Project Interpreter and click the small "+" icon in the bottom left. For each of the following, search for it in the search bar and click "Install Package".
       
       (i) numpy
      
       (ii) flask
      
       (iii) flask_restful
       
       (iv) gym
      
       c) This process didn't work for me so I had to install each package through the command line:
      
           sudo apt install python3.8-distutils
           curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
           python3.8 get-pip.py
           pip3 install numpy
      
         Repeat the last line for all of the packages listed above i.e. ```pip3 install <package_name>```
      
   4. Run the demo.
      
        a) Make sure you have the other two parts of the code running (Screen Interface (https://github.com/M4rtinR/Screen-Interface-for-Robotic-Exercise-Coach) and Robot Interface (https://github.com/M4rtinR/Robot-Interface-for-Robotic-Exercise-Coach)) and have the Operator Input (https://github.com/M4rtinR/Operator-Input-for-Robotic-Exercise-Coach) installed and ready to run.
        
        b) Click the "run" button on PyCharm. NOTE: run this code after the screen interface and robot interface are already running.
      
        c) Run the Operator Input component, and press the enter key for each repetition of an exercise that the user performs, as prompted in the standard output window and explained in the README for the Operator Input component.
      
   5. You can adjust the volume of Pepper through Choregraphe:
        
        a) Click the green "Connect to" button in the top task bar.
      
        b) If you are connected to the same network as Pepper, it should pop up. Simply click it and click "Select" in the bottom right.
      
        c) Adjust the volume to the required level using the speaker icon in the top right.

