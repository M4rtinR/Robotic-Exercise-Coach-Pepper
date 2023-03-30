# Squash and Stroke Rehabilitation Coaching Robot

This repo contains code for running both the squash coaching and stroke rehabilitation systems on Pepper. This README is written with the intention to allow people from Heriot-Watt University and the National Robotarium to run the systems as demonstrations. However, it should also provide enough information for anyone external to this group to get things up and running and start editing the code.

Below is the initial steps required for both demonstrations so please follow these first. Specific instructions for running the squash demo can be found below. For detailed instructions on how to install and run the stroke rehabilitation demo, see the "long-term stroke" branch.

The demonstrations are the same code as was used for the evaluations of the system with participants so should be fairly robust. However, they are a bit complex to set up and run and the code is a bit hacked together in places. A description of the studies run and the background to the project can be found in the demos folder in Dropbox: <Insert Link>. For externals, any publications coming from this system will be listed in the publications section below to provide background about the project.

NOTE: The demonstrations will only work on the ITT group's Pepper (the one with the "EM1.69" sticker on the back) due to different tablet versions on the other Peppers. They are set up to work with the ITT Pepper router at the moment. If you wish to run the demos through a different network, you will have to update various IP addresses - this is explained further in the individual README's of the demos.
  
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
    
      a) Visit https://www.jetbrains.com/pycharm/download/other.html and scroll down to v2020.3. The newest version of PyCharm no longer support the required Python versions used for this project.
      
      b) Extract the contents of the tar file to the location of your choice.
      
      c) Run Pycharm by opening a terminal, navigating to {extract_location}/bin, and typing ```./pycharm.sh```.
      
  4. Android Studio v 2021.3 (squash only)
    <Instructions on downloading and installing Android Studio>
    
      a) For instructions on how to download and install Android Studio, please see the GitHub pages for the racket sensor application: https://github.com/M4rtinR/racketware_app. Due to NDA agreements, this can only be shared with those at Heriot-Watt University or the National Robotarium. If you fall under this category and need access to run the demo, please contact martinross313@gmail.com.
      
  5. Choregraphe v2.5.10.7
    <Instructions on downloading and installing Choregraphe>
      
      a) The version of Choregraphe you install will depend on the version of the Naoqi operating system that is installed on the particular Pepper robot you are using. For the ITT Pepper robot, we want version 2.5.10.7, which can be downloaded via the Heriot-Watt internal Dropbox: https://www.dropbox.com/home/ITT%20Group%20team%20folder/Choregraphe/Alternative/Version%202.5.
      
      b) Download and run the Linux file: choregraphe-suite-2.5.10.7-linux64-setup.run. You may need to adjust the permissions of the file to allow it to be executed: right click the downloaded file and select Permissions, and on the permissions tab check the box labelled "Allow executing file as program". Then open the folder in a terminal window and execute ```./choregraphe-suite-2.5.10.7-linux64-setup.run```
      
      c) Follow the installation wizard to install Choregraphe.
      
      d) Enter the license key when prompted, which can be found in the licensekey.txt file on Dropbox: https://www.dropbox.com/home/ITT%20Group%20team%20folder/Choregraphe/Alternative?preview=license+key.txt
  ### Downloading components
  The demonstrations are split into multiple different components which communicate through API's. The following are all of the dmoain independent components:
  #### 1. Coaching Policies <Need to update this name>
  This is the current repo and is where the main program is stored. It does everything to do with the policies, deciding what action to take, RL to adapt the policies, behaviour tree to track the place within the session etc. Written in Python 2.
      
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
  
  You should now be able to select the required branch for the particular demo you wish to run (NOTE: the master branch contains the squash system).
  #### 2. Robot Test: <Need to update this name> https://github.com/M4rtinR/RobotTest
  This is where the interaction with the user is done through Pepper. All of the actions are sent here to be conducted by Pepper and any use of Pepper's touch sensors/limbs is dealt with here. Written in Python 2.
      
  Similar to component 1 above, clone the robot test repo into a new Pycharm project. You should then be able to select the required branch for the particular demo you wish to run.
  #### 3. Rehab Interface: <Need to update this name> https://github.com/M4rtinR/RehabInterface
  This is where the display on Pepper's tablet computer screen and interaction with the screen from the user is handled. Written in Python 3.
      
  For this component you will need to run Pycharm as an administrator. In a terminal, open the folder in which Pycharm is installed (for me this is /snap/pycharm-community/current/bin) and use the following command:
  ```sudo ./pycharm.sh```
  and enter your password when prompted. Now clone the rehab interface repo into your admin-run Pycharm as above and you should be able to select the required branch for the particular demo you wish to run.
  
  ### Domain-Dependent Components
  ### 1. Racket Sensor app <Insert link here>
      This particular branch contains the code for the squash system, so an additional component is needed. The racket sensor app is where the processing of the raw racket sensor data is done. Written in Kotlin.
  
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
       (ii) Next, add the newly installed library as a source folder to your project. Go to File -> Settings -> Project Structure. Click "Add Content Route" and point to <install folder>/task_behaviour_engine/src. You will need to do this in each branch you want to use the code from.
       
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
      
        a) Make sure you have the other two parts of the code running (screen interface (link) and robot interface (link)) and have the racket sensor app open on the home page with the sensor turned on.
        
        b) Click the "run" button on PyCharm. NOTE: run this code last (after the screen interface and robot interface are already running).
      
    5. You can adjust the volume of Pepper through Choregraphe:
        
        a) Click the green "Connect to" button in the top task bar.
      
        b) If you are connected to the same network as Pepper, it should pop up. Simply click it and click "Select" in the bottom right.
      
        c) Adjust the volume to the required level using the speaker icon in the top right.
           
## Publications

* M. K. Ross, F. Broz, and L. Baillie, “Observing and Clustering Coaching Behaviours to Inform the Design of a Personalised Robotic Coach,” in Proceedings of the 23rd International Conference on Human-Computer Interaction with Mobile Devices and Services, Virtual (originally Toulouse, France), Sep. 2021. doi: 10.1145/3447526.3472043.
