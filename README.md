# __Visualising-a-Large-Music-Collection-Based-on-its-Chord-Content__
__MSc. Project__

# Quickstart

### 1. Install requirements.

```
$ pip install -r requirements.txt
```

### 2. Start the Flask development server.

```
$ python3 Project/Data/API/app.py
```

### 3. Start the client HTTP server.

Parallel coordinates:

```
$ python3 -m http.server --bind 127.0.0.1 --directory "Project/Visualisation/Parallel/ParallelCoords"
```

Circular layout:

```
$ python3 -m http.server --bind 127.0.0.1 --directory "Project/Visualisation/Circular/CircularLayout"
```