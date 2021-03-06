# unblock-me-solver
---
This repository provides a solver for the [Unblock Me](https://play.google.com/store/apps/details?id=com.kiragames.unblockmefree&hl=en) puzzle game. See the solver in action in this [video](https://www.youtube.com/watch?v=7-QurCubPWM)!

### Method

We will connect a computer to the Android device and relay commands using the [Android Debug Bridge](https://developer.android.com/studio/command-line/adb.html) (ADB)

The steps performed by the script are: 
 - Take a screenshot on the phone
 - Transfer it to the computer
 - Process the image to obtain the start state
 - Breadth First Search (BFS) to find the solution
 - Obtain swipe commands and relay them to the phone

### Requirements:
    matplotlib
    numpy
    Android phone with a 1080x1920 resolution

### Instructions

- Follow the steps [here](https://developer.android.com/studio/command-line/adb.html) and make sure you can relay simple touch/swipe commands to your Android device.
- Open the game on the phone
- On the terminal, run

    ```shell
    $ python -u main.py
    ```

That's it! Watch the puzzles being solved automatically!

As a bonus, the solver also automatically skips ads by using a timeout to terminate BFS and pressing the back button. We can also recover from unintentional ad clicks by using the back button multiple times.
