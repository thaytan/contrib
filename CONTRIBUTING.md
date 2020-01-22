# How to Contribute

This project welcomes third-party code via merge requests.

You are welcome to propose and discuss enhancements using issues. Please label issues with the following labels:

- Bug: A bug in the code. Please make sure to describe thoroughly how to reproduce the bug.
- Enhancement: A proposed feature, which would improve the project somehow. 

> Branching Policy: The master branch is considered stable, at all times. Features are to be implemented on feature 
> branches, which are reviewed before being merged into master.

Please adhere to the following standards:

- Every example/source file must include correct copyright notice
- For indentation we are using spaces and not tabs
- Line-endings must be Unix and not DOS style
- Use `cargo fmt` to format code before committing

# Step-by-Step

1. Make sure you have [rust](https://www.rust-lang.org/) and [GStreamer](https://gstreamer.freedesktop.org/documentation/installing/index.html?gi-language=c) installed on your system.
2. Clone the project: `https://gitlab.com/aivero/public/gstreamer/gst-depth-meta.git` and `cd gst-depth-meta`
3. Create a new branch for you feature, please use a meaningful name: `git checkout -b my-branch-name`
4. Implement you changes, please try to keep you commits small.
5. Commit you changes: `git add src/your-files` and `git commit`. Please try to give the commits a meaningful commit subject and message.
6. Push changes to your feature branch: `git push --set-upstream origin my-branch-name` .
7. Open a merge request
    1. Navigate to https://gitlab.com/aivero/public/gstreamer/gst-depth-meta in a browser
    2. Click *Merge Requests* on the right-hand side panel
    3. Click *New merge request*
    4. Select you newly added branch as source and master as target.
    5. Click *Compare branches and continue*
    6. Give your merge request a meaningful name. Please prepend the name with *WIP:* if you're not done with the changes yet.
    7. Describe the changes you've made, and optimally how to test them.
    8. Submit the merge request.
8. Thank you for contributing. We'll review your changes as soon as possible.
