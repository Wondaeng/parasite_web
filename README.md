# parasite_web

<h2>Directories</h2>

<p>static directory is for the css, js, and uploaded image files.</p>
<p>template directory is for html files rendered via Flask.</p>


<h2>How to Use</h2>

<p>```bash
  python app.py
  ``` 
  to run the server using Flask. Port is set as 5002.</p>

<p>```bash
  python worker.py
  ``` 
  to run the worker. It regularly checkes the difference between the user_data and results folder.</p>

<h2>Requirements</h2>

Check the [requirements.yaml](requirements.yaml) exported from Anaconda.
