# Squash and Stroke Rehabilitation Coaching Robot

This repo contains code for running squash coaching and stroke rehabilitation systems on Pepper. The purpose of these systems and the project as a whole, is to research the effects of using a robot to guide a user through individual exercise across multiple domains, when a coach/physiotherapist is not available. To provide a detailed background of the system, any publications coming from this repo will be listed in the publications section below.

This README is written with the intention to guide anyone external to the project in getting the system up and running and starting to edit the code for their own purposes. If you are interested only in running one of the systems, or are from Heriot-Watt University/The National Robotarium and looking to demo the systems, please refer to the "long-term squash" or "long-term stroke" branch.

Below are the initial steps required for both systems so please follow these first. Next is an outline of the code and where changes are required to allow adaption to other domains. The majority of the code (other than the domain specific parts which have been removed from the master branch and can be found in the "long-term squash" and "long-term stroke" branches respectively) was used for evaluations of the system with participants so should be fairly robust. However, it is a bit complex to set up and run and the code is a bit hacked together in places. 

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
    
      a) Visit https://www.jetbrains.com/pycharm/download/other.html and scroll down to v2020.3. The demos might work with newer versions of PyCharm but I haven't tested it.
      
      b) Extract the contents of the tar file to the location of your choice.
      
      c) Run Pycharm by opening a terminal, navigating to {extract_location}/bin, and typing ```./pycharm.sh```.
      
  4. Android Studio v 2021.3 (squash only)
    <Instructions on downloading and installing Android Studio>
    
      a) For instructions on how to download and install Android Studio, please see the GitHub pages for the racket sensor application: https://github.com/M4rtinR/racketware_app. Due to NDA agreements, this can only be shared with those at Heriot-Watt University or the National Robotarium. If you fall under this category and need access to run the demo, please contact martinross313@gmail.com.
      
  5. Pepper robot running NAOqi 2.5
  
      a) Newer versions of the NAOqi operating system may not work. Additionally, different tablet versions may cause the display to be altered. For more details on this, see the README for the Screen Interface for Robotic Exercise Coach component (https://github.com/M4rtinR/Screen-Interface-for-Robotic-Exercise-Coach).
      
  6. Choregraphe v2.5.10.7
    <Instructions on downloading and installing Choregraphe>
      
      a) The version of Choregraphe you install will depend on the version of the NAOqi operating system that is installed on the particular Pepper robot you are using. For the robot used in our research, we used version 2.5.10.7. You can download any version of Choregraphe and the SDK for Python here: https://www.aldebaran.com/en/support/pepper-naoqi-2-9/downloads-softwares/former-versions.
      
      b) Download and run the Linux file: choregraphe-suite-2.5.10.7-linux64-setup.run. You may need to adjust the permissions of the file to allow it to be executed: right click the downloaded file and select Permissions, and on the permissions tab check the box labelled "Allow executing file as program". Then open the folder in a terminal window and execute ```./choregraphe-suite-2.5.10.7-linux64-setup.run```
      
      c) Follow the installation wizard to install Choregraphe.
      
      d) Enter a valid license key when prompted
  ### Downloading components
  Both the squash coaching system and the stroke rehabilitation coaching system are split into multiple different components which communicate through API's. The following are all of the dmoain independent components that you will also have to download if you want to adapt the system for your own purposes:
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
      
  c) Next, enter the URL of the repository you want to download (e.g. https://github.com/M4rtinR/Robotic-Exercise-Coach-Pepper.git) and click "clone". You should fork the project first into your own repository if you plan to edit the code.
      
  d) You may need to click "Trust project" before it will open in PyCharm.
  
  You should now be able to select the required branch for the particular system you wish to run (NOTE: the "long-term squash" branch contains the squash system and the stroke rehabilitation system can be run from the "long-term stroke" branch. If you want to make changes to the code to adapt the system to your own domain, remain in the "master" branch).
  #### 2. Robot Interface for Robotic Exercise Coach: https://github.com/M4rtinR/Robot-Interface-for-Robotic-Exercise-Coach
  This is where the interaction with the user is done through Pepper. All of the actions are sent here to be conducted by Pepper and any use of Pepper's touch sensors/limbs is dealt with here. Written in Python 2.
      
  Similar to component 1 above, clone the robot test repo into a new Pycharm project. You should then be able to select the required branch for the particular system you wish to run. For detailed instructions, see the README in the repo.
  #### 3. Screen Interface for Robotic Exercise Coach: https://github.com/M4rtinR/Screen-Interface-for-Robotic-Exercise-Coach
  This is where the display on Pepper's tablet computer screen and interaction with the screen from the user is handled. Written in Python 3.
      
  For this component you will need to run Pycharm as an administrator. In a terminal, open the folder in which Pycharm is installed (for me this is /snap/pycharm-community/current/bin) and use the following command:
  ```sudo ./pycharm.sh```
  and enter your password when prompted. Now clone the rehab interface repo into your admin-run Pycharm as above and you should be able to select the required branch for the particular system you wish to run. For detailed instructions, see the README in the repo.
  
  ### Domain-Dependent Components
  
  The sensing of movements on a user is domain-specific, but is an essential part in allowing the system to function properly. The following components were used in the squash and stroke rehabilitation systems respectively. The operator input module for stroke rehabilitation does not contain a sensor and is a WoZ replacement for this part of the architecture. This is therefore the best place to start if you don't have access to a sensing/vision system for your target use case.
  #### 1. Racket Sensor app: https://github.com/M4rtinR/racketware_app (Squash only)
  For the squash system an additional component is needed. The racket sensor app is where the processing of the raw racket sensor data is done. Written in Kotlin.
      
  #### 2. Operator Input for Robotic Exercise Coach: https://github.com/M4rtinR/Operator-Input-for-Robotic-Exercise-Coach (Stroke Rehabilitation only)
  For the stroke rehabilitation system an additional component is needed. The operator input replaces any sensing software used in the squash system, and allows the operator to signal completion of each exercise repitition to the robot. Written in Python 3.
  
## Running the System
   Now that you have all of the components downloaded on your machine, conduct the following steps to run the system on Pepper. NOTE: these steps are specific to the "long-term squash" branch but are included here as they contain information that will help you when coding and running your own system.
      
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
      
   4. Run the system.
      
        a) Make sure you have the other two parts of the code running (Screen Interface (https://github.com/M4rtinR/Screen-Interface-for-Robotic-Exercise-Coach) and Robot Interface (https://github.com/M4rtinR/Robot-Interface-for-Robotic-Exercise-Coach)) and have the racket sensor app open on the home page with the sensor turned on.
        
        b) Click the "run" button on PyCharm. NOTE: run this code last (after the screen interface and robot interface are already running).
      
   5. You can adjust the volume of Pepper through Choregraphe:
        
        a) Click the green "Connect to" button in the top task bar.
      
        b) If you are connected to the same network as Pepper, it should pop up. Simply click it and click "Select" in the bottom right.
      
        c) Adjust the volume to the required level using the speaker icon in the top right.
        
## Code Structure

## Adapting the Code to Other Domains/Use Cases
           
## Publications

* M. K. Ross, F. Broz, and L. Baillie, “Observing and Clustering Coaching Behaviours to Inform the Design of a Personalised Robotic Coach,” in Proceedings of the 23rd International Conference on Human-Computer Interaction with Mobile Devices and Services, Virtual (originally Toulouse, France), Sep. 2021. doi: 10.1145/3447526.3472043.
