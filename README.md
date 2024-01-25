# Squash and Stroke Rehabilitation Coaching Robot

This repo contains code for running squash coaching and stroke rehabilitation systems on Pepper. The purpose of these systems and the project as a whole, is to research the effects of using a robot to guide a user through individual exercise across multiple domains, when a coach/physiotherapist is not available. To provide a detailed background of the system, any publications coming from this repo will be listed in the publications section below.

This README is written with the intention to guide anyone external to the project in getting the system up and running and starting to edit the code for their own purposes. If you are interested only in running one of the systems, or are from Heriot-Watt University/The National Robotarium and looking to demo the systems, please refer to the "long-term squash" or "long-term stroke" branch. It is recommended to start with the "long-term stroke" branch because this does not require any external sensors.

Below are the initial steps required for both systems so please follow these first. Next is an outline of the code and where changes are required to allow adaption to other domains. The majority of the code (other than the domain specific parts which have been removed from the master branch and can be found in the "long-term squash" and "long-term stroke" branches respectively) was used for evaluations of the system with participants so should be fairly robust.

NOTE: There are limitations to running the demonstrations in simulation or with physical robots other than the ITT group's Pepper (the one with the "EM1.69" sticker on the back) due to different tablet versions on other Peppers. These limitations are explained in the "Running the System" section below. The demonstrations are set up to work with the ITT Pepper router at the moment. If you wish to run the demos through a different network, you will have to update various IP addresses - this is explained further in the individual README's of the demos.
  
## Instructions for Installing and Running (applicable to both squash and rehabilitation)
  ### Requirements
  1. Ubuntu 16.04 (newer versions no longer support the required Naoqi Python SDK for Pepper).
     
     a) (Reommended) You can install Ubuntu alongside Windows (dual-boot) by following the instructions here: https://itsfoss.com/install-ubuntu-1404-dual-boot-mode-windows-8-81-uefi/
     
      (i) I found that it wasn't necessary to conduct "Step 4: Make some free space on your disk for Ubuntu installation" because the Ubuntu installer will partition your hard drive automatically during installation.

     OR

     b) You can install Ubuntu through a virtual machine by following the instructions here: https://medium.com/@tushar0618/install-ubuntu-16-04-lts-on-virtual-box-desktop-version-30dc6f1958d0
  3. Python 2 and Python 3 (some parts of the Naoqi SDK only work with Python 2 and some other functionality requires Python 3).
      
      a) Python 2 should already be installed with Ubuntu 16.04. You can check which version you have by typing ```python -V``` into a terminal window.
      
      b) Python 3.5 may also be installed with Ubuntu 16.04. However, support of Python 3.5 in some of the required modules is no longer available so we need a newer version. Installing newer versions of Python is slightly more complicated in 16.04 than in newer versions of Ubuntu, but you can do it by building from source using the following commands in a terminal window:
      
         sudo apt update
         sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev
         wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tgz
         tar -xf Python-3.8.0.tgz
         cd Python-3.8.0
         ./configure --enable-optimizations
         make -j 8
         sudo make altinstall
      
      c) You can verify the installation was successful by typing ```python3.8 -V``` into a terminal window.
  4. Pycharm v2020.3
    <Instructions on downloading and installing Pycharm>

    NOTE: this is not required. You can run the required modules through a terminal window but if you are more used to a GUI then installing PyCharm is recommended. The remainder of this README is written assuming that you are using the PyCharm GUI to run the code.
    
      a) Visit https://www.jetbrains.com/pycharm/download/other.html and scroll down to v2020.3. The code should work with newer versions of PyCharm but this is untested.
      
      b) Extract the contents of the tar file to the location of your choice.
      
      c) Run Pycharm by opening a terminal, navigating to {extract_location}/bin, and typing ```./pycharm.sh```.
      
  5. Android Studio v 2021.3 (squash only)
    <Instructions on downloading and installing Android Studio>
    
      a) For instructions on how to download and install Android Studio, please see the GitHub pages for the racket sensor application: https://github.com/M4rtinR/racketware_app. Due to NDA agreements, this can only be shared with those at Heriot-Watt University or the National Robotarium. If you fall under this category and need access to run the demo, please contact martinross313@gmail.com.
      
  6. Pepper robot running NAOqi 2.5

     NOTE: it is possible to run the code in simulation without a Pepper robot but with limitations. See the "Running the System" section for details.
  
      a) Newer versions of the NAOqi operating system may not work. Additionally, different tablet versions may cause the display to be altered. For more details on this, see the README for the Screen Interface for Robotic Exercise Coach component (https://github.com/M4rtinR/Screen-Interface-for-Robotic-Exercise-Coach).
      
  8. Choregraphe v2.5.10.7
    <Instructions on downloading and installing Choregraphe>

    NOTE: Choregraphe is not necessary for running the code on a robot but is necessary if you want to run in simulation, and is also useful for testing and debugging connections with the robot.
      
      a) The version of Choregraphe you install will depend on the version of the NAOqi operating system that is installed on the particular Pepper robot you are using. For the robot used in our research, we used version 2.5.10.7. You can download any version of Choregraphe and the SDK for Python here: https://www.aldebaran.com/en/support/pepper-naoqi-2-9/downloads-softwares/former-versions.
      
      b) Download and run the Linux file: choregraphe-suite-2.5.10.7-linux64-setup.run. You may need to adjust the permissions of the file to allow it to be executed: right click the downloaded file and select Permissions, and on the permissions tab check the box labelled "Allow executing file as program". Then open the folder in a terminal window and execute ```./choregraphe-suite-2.5.10.7-linux64-setup.run```
      
      c) Follow the installation wizard to install Choregraphe.
      
      d) Enter a valid license key when prompted
  ### Downloading components
  As per the architecture diagram below, both the squash coaching system and the stroke rehabilitation coaching system are split into multiple different components which communicate through API's:
     
![Architecture Diagram for the robotic exercise coach](/Diagrams/Architecture%20Diagram%20-%20Generic.png?raw=true)
      
  The following are all of the dmoain independent components that you will also have to download if you want to adapt the system for your own purposes:
  #### 1. Robotic Exercise Coach - Pepper
  This is the current repo and is where the main program is stored. It does everything in the processing layer. It decides what action to take, contains RL to adapt the policies, and includes the behaviour tree to track the place within the session etc. Written in Python 3.
      
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
  This is where the interaction with the user is done through Pepper. It is part of the interface layer. All of the actions are sent here to be conducted by Pepper and any use of Pepper's touch sensors/limbs is dealt with here. Written in Python 2.
      
  Similar to component 1 above, clone the robot test repo into a new Pycharm project. You should then be able to select the required branch for the particular system you wish to run. For detailed instructions, see the README in the repo.
  #### 3. Screen Interface for Robotic Exercise Coach: https://github.com/M4rtinR/Screen-Interface-for-Robotic-Exercise-Coach
  This is where the display on Pepper's tablet computer screen and interaction with the screen from the user is handled. It is part of the interface layer. Written in Python 3.
      
  For this component you will need to run Pycharm as an administrator. In a terminal, open the folder in which Pycharm is installed (for me this is /snap/pycharm-community/current/bin) and use the following command:
  ```sudo ./pycharm.sh```
  and enter your password when prompted. Now clone the rehab interface repo into your admin-run Pycharm as above and you should be able to select the required branch for the particular system you wish to run. For detailed instructions, see the README in the repo.
  
  ### Domain-Dependent Components
  
  The sensing of movements on a user is domain-specific, but is an essential part in allowing the system to function properly. These components are part of the tracking layer. The following components were used in the squash and stroke rehabilitation systems respectively. The operator input module for stroke rehabilitation does not contain a sensor and is a WoZ replacement for this part of the architecture. This is therefore the best place to start if you don't have access to a sensing/vision system for your target use case.
  #### 1. Racket Sensor app: https://github.com/M4rtinR/racketware_app (Squash only)
  The racket sensor app is where the processing of the raw racket sensor data is done. Written in Kotlin.
      
  #### 2. Operator Input for Robotic Exercise Coach: https://github.com/M4rtinR/Operator-Input-for-Robotic-Exercise-Coach (Stroke Rehabilitation only)
  The operator input replaces any sensing software used in the squash system, and allows the operator to signal completion of each exercise repitition to the robot. Written in Python 3.
  
## Running the System
   Now that you have all of the components downloaded on your machine, conduct the following steps to run the system on Pepper. NOTE: we recommend to start with the stroke rehabilitation system because this can be run without an external sensor or squash equipment. Therefore, please refer to the "long-term stroke" branch from now on. The following steps are specific to the "long-term squash" branch but are included here as they contain information that will help you when coding and running your own system.
      
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

  The code in this repo is situated within the processing layer of the architecture diagram above. This README gives an overview of the purpose of each directory and file, but more thourough documentation can be found within the code.
      
  ### CoachingBehaviourTree
      
  This directory contains all the code associated with the Controller block of the architecture diagram. It is made up of 5 python files:
     
  * config.py: This file contains all the initial values used by throughout the program, from the name, ability and motivation of the user (used for high-level personalisation) to the ip address and port number used to connect to the other components.
  * controller.py: This file is where the main behaviour tree skeleton is created. The tree follows a structure similar to this:

![Simple behaviour tree of the robotic coach](/Diagrams/Behaviour%20Tree/Behaviour%20Tree%20-%20full%20simple.png?raw=true)
      
   A much more detailed visualisation of the behaviour tree can be found in the  Diagrams/Behaviour Tree directory.
  * nodes.py: This file contains all of the leaf nodes which implement the behaviour to be used by the robot coach. All classes in this file are Behaviour Tree Nodes.
  * action.py: This file contains a data class for storing information about an action which will be performed by the robot.
  * behaviour_library.py: This script is where all of the different utterance options for the robot are stored.
  
  ### Policy
  
  This directory contains all the code associated with the Coaching Policy block of the architecture diagram. It is also where the low-level adaption is conducted to modify the starting policy to each individual user. It is made up of 3 python files:
   
  * coaching_env.py: A class which acts as a wrapper for the interaction. It steps through each episode (session) by requesting a behaviour from the policy, ticking the behaviour tree with that behaviour, and updating the policy using the reward obtained from the observations made about the current state of the session.
  * policy_wrapper.py: A class which acts as an interface between the raw policy and the coaching environment. It can return a behaviour cateogry to the coaching environment, which is generated by the policy but which is within a set of defined valid behaviours for a given state.
  * policy.py: The raw policy class which contains the original transition matrices of the 12 clustered policies learnt from observations of human-human interactions. At each timestep, it selects the next action from the transition matrix, based on the current state distribution. For more information about the observations and clustered policies, see the publications section below.
      
  ### API
  
  This directory contains the code associated with the link between the processing layer and tracking layer of the architecture diagram. It is made up of a single python file:
      
  * api_classes.py: This file contains a Flask API which handles requests from the movement analysis software block, and updates the system's configuration values based on those requests. I.e. it receives performance scores based on the user's exercises which the system can use to formulate appropriate actions.
      
## Adapting the Code to Other Domains/Use Cases

  The idea behind this repository is to increase research ouput in the area of robotic coaching by providing a system that can be adapted to different domains and use cases. The structure of the behaviour tree, the coaching policies, and the RL adaption system are all domain independent. However, if you wish to use the system in a new domain, the following changes will be required. A much more detailed explanation of the changes can be found within the python files, and within the other components of the system.
      
  * behaviour_library.py: The utterances used by the robot to guide and coach users through a session, must obviously be domain-specific. However, they can follow the same structure as the utterances used by the squash and stroke rehabilitation coaching systems if you wish. This structure selects at random one of four different options for each combination of performance, phase of session (i.e. intro, during, or feedback), goal level and behaviour category. The utterances used by the robotic coaching system have been left in the code to provide a starting point. NOTE: The specific utterances used by the system were not a focus of our research so I'm sure a better structure and better individual utterances can be designed.
  * config.py: Domain-specific setup is required in the config file. For example, variables such as ```shot``` and ```stat``` should be renamed to something more specific for the given use case. Additionally, the ```post_address``` and ```screen_post_address``` ip address variables will need to be updated, along with the initial ```ability```, ```motivation```, ```name``` etc values for each session that is run.
  * Robot Interface for Robotic Exercise Coach component (https://github.com/M4rtinR/Robot-Interface-for-Robotic-Exercise-Coach): In this component, the structure of displaying the actions can be kept as is, but new demonstrations will need to be made for the new use case.
  * Screen Interface for Robotic Exercise Coach component (https://github.com/M4rtinR/Screen-Interface-for-Robotic-Exercise-Coach): The general layout of the screen, and the subtitle process can remain as is. However, new domain-specific pictures of exercises, and options for selecting which exercise to conduct, must be updated for the new use case.
  * Tracking Layer: This is probably where the most work will be required. A sensing or vision device specific to the current domain will need to be sourced/created. The movement analysis software block of the system architecture will also need to be coded. This code should translate the raw data received from the sensor/vision system into a numeric score and pass this score, through the API defined in api_classes.py, to the coaching environment at appropriate times to use as a performance indicator from which to generate appropriate utterances and actions. NOTE: to get started without a domain-specific sensing/vision system, you can use the Operator Input for Robotic Exercise Coach component: https://github.com/M4rtinR/Operator-Input-for-Robotic-Exercise-Coach. This was used with the stroke rehabilitation system to provide a WoZ bypass to the tracking layer and allows an operator to press enter on each completed repetition of an exercise. Changes to the API are also needed for this component to plug in smoothly, so please see the code in the "long-term stroke" branch for more details.
      
## Publications

* XXXX
