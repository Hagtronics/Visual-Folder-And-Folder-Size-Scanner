# Visual Folder Size Scanner
A useful(?) utility for examining what folders / directories on a disk are taking up space.
Written in Pure Python 3.12+ with the only dependency being ttkbootstrap for a prettier GUI experience (see requirements.txt)
  
## Figure 1 – Overview of GUI  
  
## Usage:  
1) Get the code, and make sure that ttkbootstrap is installed on your system.
2) Run the code.
3) Select a folder as a starting point. After the folder is selected the directory scanning begins automatically. This may take some time, please be patient.
4) When scanning is complete, the treeview shows the folder path on the left and the folder total size on the right – the size contains the folder itself and all the folders underneath the that folder. See figure 2.
5) Right clicking on a path row will bring up a menu (figure 3) that allows you to do the listed operations.
6) The Path and Size Columns may be sorted in ascending or descending order by clicking on the ‘Path’ or ‘Size’ labels in the column header. The sort order may be reset by pressing the ‘Reset Sort’ button at the top of the form.
7) The Path/Size data may be saved to a CSV file for late use by pressing the “Save to CSV” button at the top of the form.
8) The “Toggle Theme” button toggles the theme from light to dark and back again.
  
## Figure 2 – The reported folder size is the sum of that folder and all the sub-folders. In this example, the folder that really contains the 11GB of data is the last one, the folders above it are the sum of that folder and all sub-folders. This is the same way that the Windows Explorer ‘Properties’ function works.
  
## Figure 3 – Right clicking on a ‘Row’ will bring up the following menu options.  
  
## Speed:  

I know what you are thinking…. You are thinking that using Python for a big folder walk is going to be as slow as molasses, right? Because everyone thinks that Python is the slowest language on the face of the Earth right? 

Let’s examine the facts,

I sent this program on my entire 190,000 ‘User’ directory of my PC. This program took 34 Seconds to complete the task.

I wrote a similar program in compiled C# .NET 8, and it took 122 Seconds to traverse the same folders! I had to add multi-threading parallel-for elements to the C# program which got the time down to 25 Seconds. This is really only marginally faster than the Python program.

Interestingly, the C# Parallel For-Loop also spins up all 12 threads of my notebook to 100% and makes the fans start, something the Python program does not do. All that to get a marginal gain.

Enjoy!

