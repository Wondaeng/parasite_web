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
<p>to run the worker. It regularly checkes the difference between the user_data and results folder.</p>

<h2>Requirements</h2>

Check the [requirements.yaml](requirements.yaml) exported from Anaconda.

<h2>Model</h2>
<p>The parasite model `model_best.pth` is not uploaded since it is too big (>100MB).
You can find it `/home/simmani91/web_parasite/model_best.pth` in 150 server.</p>
