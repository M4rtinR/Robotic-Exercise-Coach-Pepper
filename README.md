# Squash and Stroke Rehabilitation Coaching Robot

This repo contains code for running both the squash coaching and stroke rehabilitation systems on Pepper. Below is the initial steps required for both demonstrations so please follow these first. For detailed instructions on how to install and run each demonstration please see the "long-term squash" and "long-term stroke" branches respectively.

The demonstrations are the same code as was used for the evaluations of the system with participants so should be fairly robust. However, they are a bit complex to set up and run and the code is a bit hacked together in places. A description of the studies run and the background to the project can be found in the demos folder in Dropbox: <Insert Link>.

NOTE: The demonstrations will only work on the ITT group's Pepper (the one with the "EM1.69" sticker on the back) due to different tablet versions on the other Peppers. They are set up to work with the ITT Pepper router at the moment. If you wish to run the demos through a different network, you will have to update various IP addresses - this is explained further in the individual README's of the demos.
  
## Instructions for Installing and Running (applicable to both squash and rehabilitation)
  ### Requirements
  1. Ubuntu 16.04 (newer versions might work but I had problems with any version other than this).
    <Instructions on downloading Ubuntu and creating dual boot on Windows>
  2. Python 2 and Python 3 (not great practice I know, but some parts of the Naoqi SDK only work with Python 2 and some other functionality was a lot easier to implement in Python 3).
    <Instructions on downloading Python 2 and 3>
  3. Pycharm v2020.3
    <Instructions on downloading and installing Pycharm>
  4. Android Studio v 2021.3
    <Instructions on downloading and installing Android Studio>
  5. Choregraphe v2.5.10.7
    <Instructions on downloading and installing Choregraphe>
  ### Downloading components
  The demonstrations are split into multiple different components which communicate through API's. The following are all of the dmoain independent components:
  #### 1. Coaching Policies <Need to update this name>
  This is the current repo and is where the main program is stored. It does everything to do with the policies, deciding what action to take, RL to adapt the policies, behaviour tree to track the place within the session etc. Written in Python 2.
      
  Once you have installed Pycharm, as above, clone this repo into Pycharm as a new project.
  
  You should now be able to select the required branch for the particular demo you wish to run (NOTE: the master branch does nothing).
  #### 2. Robot Test: <Need to update this name> https://github.com/M4rtinR/RobotTest
  This is where the interaction with the user is done through Pepper. All of the actions are sent here to be conducted by Pepper and any use of Pepper's touch sensors/limbs is dealt with here. Written in Python 2.
      
  Similar to component 1 above, clone the robot test repo into a new Pycharm project. You should then be able to select the required branch for the particular demo you wish to run.
  #### 3. Rehab Interface <Need to update this name> <Insert link to repo>
  This is where the display on Pepper's tablet computer screen and interaction with the screen from the user is handled. Written in Python 3.
      
  For this component you will need to run Pycharm as an administrator. In a terminal, open the folder in which Pycharm is installed (for me this is /snap/pycharm-community/current/bin) and use the following command:
  ```sudo ./pycharm.sh```
  and enter your password when prompted. Now clone the rehab interface repo into your admin-run Pycharm as above and you should be able to select the required branch for the particular demo you wish to run.
