##################################################################
# Brian Lesko 
# 12/2/2023
# Robotics Studies, control a virtual robot with a ps5 controller

import streamlit as st
import numpy as np
import modern_robotics as mr
import matplotlib.pyplot as plt
import time
import math

import dualsense # DualSense controller communication
import customize_gui # streamlit GUI modifications
import robot
DualSense = dualsense.DualSense
gui = customize_gui.gui()
my_robot = robot.two2_robot()

def main():
    # Set up the app UI
    gui.clean_format(wide=True)
    gui.about(text = "This code implements control of a simple robot with a ps5 remote.")
    Title = st.empty()
    subTitle = st.empty()
    with st.sidebar: Sidebar = st.empty()
    progress_bar = st.progress(0)
    image_spot = st.empty()
    
    # Setting up the dualsense controller connection
    vendorID, productID = int("0x054C", 16), int("0x0CE6", 16)
    ds = DualSense(vendorID, productID)
    try: ds.connect()
    except Exception as e:
        st.error("Error occurred while connecting to Dualsense controller. Make sure the controller is wired up and the vendor and product ID's are correctly set in the python script.")
    
    # Initialize loop variables
    step = .001
    thetas = [0,0]
    prev_L1, prev_R1 = False, False
    th = robot.CyclicVariable(thetas)
    loop, loops = 0, 1000

    # Control Loop
    for i in range(loops):
        ds.receive()
        ds.updateTriggers()
        ds.updateThumbsticks()

        # Determine which joint is selected
        j1 = "<span style='font-size:30px;'>J1</span>" if th.index == 0 else "<span style='font-size:20px;'>J1</span>"
        j2 = "<span style='font-size:30px;'>J2</span>" if th.index == 1 else "<span style='font-size:20px;'>J2</span>"
        with Title: st.markdown(f" &nbsp; &nbsp; &nbsp; &nbsp;<L1/R1> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;{j1} &nbsp; | &nbsp; {j2} &nbsp; ", unsafe_allow_html=True)

        # Increment and decrement the controlled joint index based on the L1 and R1 buttons
        if ds.L1 and not prev_L1:
            th.decrement()
        if ds.R1 and not prev_R1:
            th.increment()
        prev_L1 = ds.L1
        prev_R1 = ds.R1

        # Button Control
        i = th.index
        if ds.L2 > 0:
            thetas[i] = thetas[i] + step*ds.L2/1.5
        if ds.R2 > 0:
            thetas[i] = thetas[i] - step*ds.R2/1.5

        # Thumbstick control
        ds.updateThumbsticks()
        if ds.RX > 4 or ds.RX < -4:
            with Sidebar: st.write("Desired Angle: ", math.degrees(ds.Rthumb)) # + "Current Angle: " + thetas[i]
            distance = ds.Rthumb - thetas[i]
            # Adjust distance to be between -pi and pi
            while distance < -math.pi: distance += 2 * math.pi
            while distance > math.pi:  distance -= 2 * math.pi
            thetas[i] = thetas[i] + step*333*(distance)

        # Show the robot
        fig = my_robot.get_robot_figure(thetas[0],thetas[1])
        with image_spot: st.pyplot(fig)
        progress_bar.progress(loop/loops)
        loop = loop + 1
        time.sleep(.001)

    with Title: st.write('The Control Loop has ended')
    ds.disconnect()

main()