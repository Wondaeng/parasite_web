# parasite_web

<p>static directory is for the css, js, and uploaded image files.</p>
template directory is for html files rendered via Flask.

`python app.py` to run the server using Flask. Port is set as 5002.
`python worker.py` to run the worker. It regularly checkes the difference between the user_data and results folder.
