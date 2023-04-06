# parasite_web

<h2>Directories</h2>

<p>static directory is for the css, js, and uploaded image files.</p>
<p>template directory is for html files rendered via Flask.</p>


<h2>How to Use</h2>

```bash
python app.py
```
 <p>to run the server using Flask. Port is set as 5002.</p>

```bash
python worker.py
``` 
<p>to run the worker. It regularly checks the difference between the user_data and results folder.</p>

<h2>Requirements</h2>

Check the [requirements.yaml](requirements.yaml) exported from Anaconda.
It requires Detectron2 for inference.

<h2>Model</h2>
<p>The parasite model `model_best.pth` is not uploaded since it is too big (>100MB).
You can find it `/home/gugcweb/ats/model_25.pth` in 150 server.</p>
